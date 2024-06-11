import os
import unittest

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.chatgpt.module_chatgpt import module_chatgpt
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
from gdo.chatgpt.TrainingThread import TrainingThread
from gdo.chatgpt.method.ChappyEventListener import ChappyEventListener
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Bash import Bash
from gdo.irc.method.CMD_PRIVMSG import CMD_PRIVMSG
from gdotest.TestUtil import web_plug, reinstall_module, cli_plug, cli_gizmore, install_module


class ChatTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        reinstall_module('blackjack')
        reinstall_module('chatgpt')
        reinstall_module('irc')
        loader.init_modules(True, True)
        loader.init_cli()
        return self

    def test_01_chappy_user(self):
        id = module_chatgpt.instance().cfg_chappy_id()
        self.assertIsNotNone(id, 'Cannot get chappy id.')
        user = module_chatgpt.instance().cfg_chappy()
        self.assertIsInstance(user, GDO_User, 'Cannot get chappy user.')
        self.assertEqual(id, user.get_id(), 'ID User mismatch for cfg_chappy().')

    def test_02_prompt(self):
        cli_plug(cli_gizmore(), "$chappy on")
        genome = GDO_ChatGenome.get_for_user(cli_gizmore())
        thread = TrainingThread(genome)
        GDO_ChatMessage.blank({
            'gcm_genome': genome.get_id(),
            'gcm_user': cli_gizmore().get_id(),
            'gcm_text': 'I heard there is a qubit error correction code that uses +5 extra qubits to correct one qubit error.',
        }).insert()
        GDO_ChatMessage.blank({
            'gcm_genome': genome.get_id(),
            'gcm_user': cli_gizmore().get_id(),
            'gcm_prompt': '1',
            'gcm_text': 'Chappy: Can\'t we just omit the real data bit then, and just use 5 bits to encode one instead of 6?',
        }).insert()
        thread.chatgpt_request()
        count = GDO_ChatMessage.table().count_where()
        self.assertEqual(count, 3, 'chatgpt_request() does not work.')

    def test_03_blackjack(self):
        cli_plug(cli_gizmore(), "$chappy --model=blackjack on")
        genome = GDO_ChatGenome.get_for_user(cli_gizmore())
        thread = TrainingThread(genome)
        GDO_ChatMessage.blank({
            'gcm_genome': genome.get_id(),
            'gcm_user': cli_gizmore().get_id(),
            'gcm_prompt': '1',
            'gcm_text': 'Chappy: You are in a unit tests to let you play a round of blackjack.'
                        'You need to play one full round.'
                        'Try to play as good as you can. The game is blackjack.'
                        'When you are done with the round => $ack.',
        }).insert()
        thread.chatgpt_request()
        count = GDO_ChatMessage.table().count_where()
        count2 = 0
        while count2 != count:  # play until nothing more happens.
            count2 = count
            thread.running()
            count = GDO_ChatMessage.table().count_where()
        self.assertGreaterEqual(count, 5, 'Chappy does not play blackjack long enough.')

    def test_04_irc(self):
        try:
            cli_plug(None, '$add_server giz IRC tcp://irc.giz.org:6667')
        except:
            pass
        server = GDO_Server.table().get_by_vals({
            'serv_name': 'giz',
        })
        self.assertIsNotNone(server, 'test irc server missing')
        server.get_connector().process_message(':gizmore!~kvirc@p549970e0.dip0.t-ipconnect.de PRIVMSG #dog :$chappy --model blackjack on')
        server.get_connector().process_message(':gizmore!~kvirc@p549970e0.dip0.t-ipconnect.de PRIVMSG #dog :Chappy: Please play a round of blackjack.')
        self.assertTrue(True, 'blah')


    # def test_03_fine_tuning(self):
    #     cli_plug(cli_gizmore(), "chappy on")
    #     genome = GDO_ChatGenome.get_for_user(cli_gizmore())
    #     thread = TrainingThread(genome)
    #     prompts = [
    #         'Chappy: how are you?',
    #         'Chappy: This is a test. I need 10 such tests to trigger an automated fine-training for you.',
    #         'Chappy: This is test message 3.',
    #         'Chappy: Do you still like this testing?',
    #         'Chappy: Test 5 - What is 4+1?',
    #         'Chappy: Test 6 - What is your purpose?',
    #         'Chappy: Test 7/10 - I am working on an implementation of you with the same rights as a normal user. You will be able to operate a bot as an interface.',
    #         'Chappy: how are you?',
    #         'Chappy: how are you?',
    #         'Chappy: how are you?',
    #     ]
    #     for prompt in prompts:
    #         GDO_ChatMessage.blank({
    #             'gcm_genome': genome.get_id(),
    #             'gcm_user': cli_gizmore().get_id(),
    #             'gcm_text': prompt,
    #         }).insert()
    #         thread.chatgpt_request()
    #
    #     thread.evolve()
    #     self.assertTrue(True, 'stub')


if __name__ == '__main__':
    unittest.main()
