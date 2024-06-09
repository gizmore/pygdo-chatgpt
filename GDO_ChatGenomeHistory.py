from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_DateTime import GDT_DateTime
from gdo.date.Time import Time


class GDO_ChatGenomeHistory(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('cgh_id'),
            GDT_Object('cgh_genome').table(GDO_ChatGenome.table()).not_null(),
            GDT_String('cgh_name'),
            GDT_DateTime('cgh_processed'),
            GDT_Created('cgh_created'),
        ]

    @classmethod
    def init_evolve(cls, genome: GDO_ChatGenome):
        cls.blank({
            'cgh_genome': genome.get_id(),
        }).insert()

    @classmethod
    def evolve(cls, genome: GDO_ChatGenome, model_name: str):
        entry = cls.table().get_by_vals({
            'cgh_genome': genome.get_id(),
            'cgh_name': None,
        })
        entry.save_vals({
            'cgh_name': model_name,
            'cgh_processed': Time.get_date(),
        })
        genome.evolve(model_name)
        pass

