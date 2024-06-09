from gdo.core.GDT_Float import GDT_Float


class GDT_ChatTemperature(GDT_Float):
    DETERMINISTIC = '0.0'
    DEFAULT = '0.1'
    MODERATE = '0.4'
    RANDOM = '1.0'

    def __init__(self, name: str):
        super().__init__(name)
        self.min(0).max(1)
        self.initial(self.DETERMINISTIC)
