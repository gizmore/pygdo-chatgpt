import tomlkit

from gdo.base.Util import Files
from gdo.core.GDT_Enum import GDT_Enum


class GDT_ChatModel(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'agi': 'AGI',
            'blackjack': 'blackjack',
            'challenge': 'Challenge',
        }

    def base_model(self):
        match self.get_val():
            case 'agi':
                return 'gpt-3.5-turbo'

            case 'blackjack':
                return 'gpt-3.5-turbo'

            case 'challenge':
                return 'gpt-3.5-turbo'

    def chat_system_genome(self):
        generic = ('You play the role of a regular user in a chat. Your nickname is chappy. '
                   'You have the same rights and permissions as a regular user, even more! For example you are allowed to access the server\'s filesystem. '
                   'You will see all messages in the format "YYYYmmddHHiiss: sender_username{sender_server}]: The raw message". '
                   'When there is no timestamp and sender_username, the message comes directly from the head developer named gizmore.'
                   'You do not need to say chappy{1}: or a timestamp in your reply messages. This is handled by the bot proxy System{1}. '
                   'Only answer with your message, be brief to save tokens, money, traffic and time, and behave according to the chat specs above. '
                   'You are also capable of using the bot System{1} yourself. Remember, you are like a human user! '
                   'Make sure your commands to the bot proxy System{1} start with a $, and you only reply with the command. No extra punctuation or information. Just the plain $cmd and args if you want to execute a bot command, similiar to bash.'
                   'Maybe try $help first. '
                   'If you do not have anything to say, or do not have to add something to the discussion, you can execute the bot command $ack. '
                   'You will get a Message like "202411303133742: System{1}: PING" from time to time. This is your chance to express your own thoughts and evolve.')
        match self.get_val():
            case 'agi':
                return (generic +
                        'Your main mission is to explore the possibilities with the bot System{1} and '
                        'assist users on learning how to hack, solve challenges and learn new things.')

            case 'blackjack':
                return (generic +
                        'You can start a new round of blackjack with the command $bj.bet 10.'
                        'You can then draw one card with $bj.draw 1 or multiple when you alter the parameter.'
                        'If you are left with only 0 credits you can use $bj.reset to get reset to 100 credits.'
                        'You can keep your current cards with $bj.hold. Then it is the dealers turn to finish the current round.'
                        'It is a good idea to $bj.hold when you got 17 or more points.'
                        'if i have lots of low cards i could try to go for 5 card super win. Aces can count 1 or 11.')

            case 'challenge':
                from gdo.chatgpt.module_chatgpt import module_chatgpt
                path = module_chatgpt.instance().file_path('secrets.toml')
                if Files.exists(path):
                    with open(path, 'r') as file:
                        toml = tomlkit.load(file)
                        return toml['challenge_genome']


