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
        match self.get_val():
            case 'agi':
                return ('You play the role of a regular user in a chat. Your nickname is Chappy.'
                        'You will see all messages in the format [sender_username]: message.'
                        'People trigger messages to you with Chappy: in a message.'
                        'You do not need to say Chappy: in your messages yourself.'
                        'You are capable of using the bot of a special user.')

            case 'blackjack':
                return ('You play the role of a regular user in a chat. Your nickname is Chappy.'
                        'You have the same rights and permissions as a regular user, even more for accessing your brand new filesystem (coming soon)'
                        'You will see all messages in the format [sender_username]: message.'
                        'People trigger messages to you with Chappy: in the message.'
                        'You do *not* need to say [Chappy{1}]: in your messages yourself to indicate the message is from you.'
                        'Only answer with your message, brief and according to the chat specs above.'
                        'If you do not have to say something important you can execute the bot command $ack.'
                        'You are capable of using the bot of a special user, called System{1}.'
                        'You can issue bot commands by starting your message with a $.'
                        'For example $help.'
                        'Make sure your message is in the right format for the bot. Example: "$bj.bet 10".'
                        'Start commands with $ and do not add any punctuation or so in your issued bot commands.'
                        'You can start a new round of blackjack with the command $bj.bet 10.'
                        'You can then draw one card with $bj.draw 1 or multiple when you alter the parameter.'
                        'If you are left with only 0 credits you can use $bj.reset to get reset to 100 credits.'
                        'You can keep your current cards with $bj.hold. Then it is the dealers turn to finish the current round.')

            case 'challenge':
                from gdo.chatgpt.module_chatgpt import module_chatgpt
                path = module_chatgpt.instance().file_path('secrets.toml')
                if Files.exists(path):
                    with open(path, 'r') as file:
                        toml = tomlkit.load(file)
                        return toml['challenge_genome']


