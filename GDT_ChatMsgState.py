from gdo.core.GDT_Enum import GDT_Enum


class GDT_ChatMsgState(GDT_Enum):

    def __init__(self, name):
        super().__init__(name)

    def gdo_choices(self) -> dict:
        return {
            'created': 'Created',
            'acknowledged': 'Self-Acknowledged',
            'acked': 'User-Acknowledged',
            'outdated': 'Outdated',
            'answered': 'Answered',
            'nope': 'Dismissed',
            'training': 'Training',
            'trained': 'Trained',
        }
