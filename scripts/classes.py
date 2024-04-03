from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass, field, fields, asdict, astuple
from datetime import datetime
from math import inf
from os import makedirs
from os.path import exists
from pathlib import Path
from random import shuffle
from secrets import choice
from string import ascii_letters, digits
from typing import Any, Literal, Self, Type

from dacite import from_dict
from ujson import dumps, loads, JSONDecodeError

from .config import *
from .functions import *
from libs.vk_api_fast.keyboard import VkKeyboard


__all__ = ['botPrefs', 'DictLikeClass', 'BotPrefs', 'VersionInfo', 'Users', 'BaseUser']


@dataclass
class VersionInfo:
    full: str = f'1.0.0indev06.00 (000000.0-0600.{datetime.now():{Constants.DateTimeForms.forVersion}})'
    name: str = 'Release'
    changelog: str = (
        '\n\n❕1.0.0r'
        '➕Initial release'
    )

    def __post_init__(self):
        self.main = '.'.join(self.full.split('.')[:2])


@dataclass(slots=True)
class DictLikeClass(Collection):
    def get(self, field_: str):
        return getattr(self, field_)

    def set(self, field_: str, value: Any) -> None:
        setattr(self, field_, value)

    def inc(self, field_: str) -> None:
        setattr(self, field_, self.get(field_) + 1)

    @property
    def fields(self) -> list[str]:
        return [field_.name for field_ in fields(self)]

    @property
    def values(self) -> list[Any]:
        return [getattr(self, field_.name) for field_ in fields(self)]

    @property
    def toDict(self) -> dict[str, Any]:
        return asdict(self)

    def toFile(self, file_path: Path | str) -> None:
        with open(file_path, 'w') as file:
            file.write(dumps(self.toDict, indent=4, escape_forward_slashes=False))

    @classmethod
    def fromDict(cls, dictionary: dict[str, Any]) -> Self:
        return from_dict(cls, dictionary)

    @classmethod
    def fromFile(cls, file_path: Path | str) -> Self:
        if not exists(file_path):
            return cls()
        try:
            with open(file_path) as f:
                return cls.fromDict(loads(f.read()))
        except JSONDecodeError:
            return cls()

    def __contains__(self, item: Any):
        return item in {field_ for field_, _ in self}

    def __len__(self):
        return len(fields(self))

    def __iter__(self):
        yield from ((field_.name, getattr(self, field_.name)) for field_ in fields(self))


@dataclass(slots=True)
class Exercise(DictLikeClass):
    name: str
    description: str
    animationPath: Path


@dataclass(slots=True)
class BenchPressDumbbellsLying(Exercise):
    name: str = 'Bench_press_dumbbells_lying'
    description: str = 'В чем польза: Представленное упражнение для мужчин в домашних условиях также относится к разряду базовых, поскольку оно крайне эффективно работает в вопросах наращивания объема груди. Жим гантелей практически ничем не отличается от жима штанги, становясь отличной альтернативой как в домашних условиях, так и в зале.\nКак выполнять: Жим производится лежа на специальной скамейке. Для начала возложите вес на грудь продольным хватом, после чего с усилием выжимайте его перед собой, не допуская закрытия локтевого замка. Опускайте гантели обратно медленно, без резких движений или бросков.'
    animationPath: Path = Path('exercises', 'Bench_press_dumbbells_lying.gif')


@dataclass(slots=True)
class BenchPressDumbbellsSitting(Exercise):
    name: str = 'Bench_press_dumbbells_Sitting'
    description: str = 'В чем польза: Тренировка для мужчин на плечи начинается с базового жима сидя. Это элемент, развивающий объем и силу дельтоидов. Это технически простое движение, не оказывающее лишней нагрузки на позвоночник. С легким весом можно работать хоть каждый день — никаких перегрузок вы не испытаете.\nКак выполнять: Для работы желательно использовать стул с высокой спинкой. Сядьте на него, выпрямите спину. Вес поднимите так, будто удерживаете гриф штанги. После этого выжимайте снаряды над головой, не допуская защелкивания локтевого замка. В процессе движения предплечья всегда перпендикулярны полу.'
    animationPath: Path = Path('exercises', 'Bench_press_dumbbells_Sitting.gif')


@dataclass(slots=True)
class BenchPressLying(Exercise):
    name: str = 'Bench_press_lying'
    description: str = 'В чем польза: Упражнение развивает верхнюю часть тела, увеличивая силу рук и плеч, а также формирует рельеф в области груди. Кроме того, жим лежа способствует растягиванию грудных, что увеличивает их эластичность и потенциал к росту.\nКак выполнять: Жим лежа выполняется на прямой или наклонной скамье со стойками для грифа. Для выполнения лягте на скамью и возьмите гриф прямым закрытым хватом. Расстояние между ладонями должно быть чуть шире плеч. Опустите штангу к груди, разводя локти в стороны до параллели с полом. Затем выжмите гриф вверх, выпрямляя руки. Во время жима локти должны быть согнуты под прямым углом и смотреть в стороны, а не вниз.'
    animationPath: Path = Path('exercises', 'Bench_press_lying.gif')


@dataclass(slots=True)
class BendingHandsWithRod(Exercise):
    name: str = 'Bending_hands_with_rod'
    description: str = 'В чем польза: Сгибание рук на бицепс поможет вам увеличить руки в объеме и укрепить плечевой пояс. Кроме того, упражнение улучшает кровообращение в верхней части тела и стимулирует метаболизм.\nКак выполнять: Для выполнения возьмите штангу обратным хватом и опустите прямые руки вниз, согнув их немного в локтях. Теперь сгибайте руки с полной амплитудой, приводя штангу к груди. В нижней точке оставляйте локти немного согнутыми, что поможет предотвратить травмы. Выполняйте упражнение медленно без резких движений, сосредоточившись на напряжении бицепсов рук.'
    animationPath: Path = Path('exercises', 'Bending_hands_with_rod.gif')


@dataclass(slots=True)
class BreedingDumbbellsLying(Exercise):
    name: str = 'Breeding_dumbbells_lying'
    description: str = 'В чем польза: Целевой группой при работе являются большие грудные мышцы. Они практически полностью изолируются в процессе работы. Поскольку бицепс и трицепс помогает удерживать гантели в определенном положении, на них тоже приходится определенная часть нагрузки. Ягодицы, живот и мелкие мышцы корпуса удерживают тело неподвижно.\nКак выполнять: Разводите вес до уровня, пока не почувствуете приличное натяжение в области груди. Не нужно перебарщивать, опуская снаряды до боли в плечах — это опасно. Разведение выполняется в среднем темпе без резких рывков. Руки всегда держите в слегка согнутом положении.'
    animationPath: Path = Path('exercises', 'Breeding_dumbbells_lying.gif')


@dataclass(slots=True)
class FightingHandsTilt(Exercise):
    name: str = 'Fighting_hands_Tilt'
    description: str = 'В чем польза: В качестве агонистов выступают локтевые мышцы и трицепсы. В качестве стабилизаторов используются задние пучки дельт, а также разгибатели плеча. Статической нагрузке поддается поясничная группа мышц. Упражнение идеально подходит и новичкам, и профессионалам.\nКак выполнять: Упражнение, входящее в программу для мужчин на неделю, делается в наклоне. Соблюдайте небольшой полуприсед. Руки необходимо держать прижатыми к бокам корпуса. Разгибайте верхние конечности до уровня, пока они не образуют прямую линию. Напряжение при этом сосредотачивается в трицепсах.'
    animationPath: Path = Path('exercises', 'Fighting_hands_Tilt.gif')


@dataclass(slots=True)
class FrenchBenchPressLying(Exercise):
    name: str = 'French_bench press_lying'
    description: str = 'В чем польза: Французский жим способствует набору массы в верхней части рук, формируя внушительный рельеф. Также упражнение укрепляет суставы, улучшая их подвижность и стабилизируя их за счет роста мышц.\nКак выполнять: Чтобы выполнить упражнение, возьмите гриф прямым хватом и лягте на прямую скамью без стоек. Поднимите штангу над собой и согните руки в локтях, опуская гриф за голову. Не сгибайте локти более чем на 90 градусов, чтобы не травмировать плечи. Выполняйте упражнение осторожно в медленном темпе, акцентируя внимание на работе задней части рук. Для упражнения подойдет не только прямой, но и Z-гриф.'
    animationPath: Path = Path('exercises', 'French_bench_press_lying.gif')


@dataclass(slots=True)
class Pushups(Exercise):
    name: str = 'Pushups'
    description: str = 'В чем польза: Это базовое упражнение для дома, являющееся одним из самых популярных среди упражнений с весом собственного тела. Оно эффективно развивает объемы и силу груди и трицепсов, являясь при этом минимально травмоопасным упражнением.\nКак выполнять: Примите классический упор лежа, расположив ладони немного шире уровня ключиц. Отжимание выполняйте до уровня, пока грудь не окажется в 2-3 см от пола. Локти старайтесь прижимать к бокам и направлять назад.'
    animationPath: Path = Path('exercises', 'Pushups.gif')


@dataclass(slots=True)
class SquatsWithRod(Exercise):
    name: str = 'Squats_with_rod'
    description: str = 'В чем польза: Приседания с весом укрепляют мышцы кора и нижней части тела, а также суставно-связочный аппарат, увеличивают силу и выносливость организма, улучшают баланс и координацию движений, формируют красивый рельеф ног и ягодиц.\nКак выполнять: Если вы тренируетесь в зале, то это упражнение со штангой лучше выполнять в силовой раме. Положите гриф на область трапеций. Упритесь пятками в пол и начинайте приседание. Подбородок приподнят, плечи развернуты, спина прямая. Отводите таз максимально назад, не сгибаясь в пояснице. Приседайте до параллели с полом, следите, чтобы носки находились на уровне коленей. Не подворачивайте таз при подъеме и держите колени немного согнутыми, чтобы снизить на них нагрузку.'
    animationPath: Path = Path('exercises', 'Squats_with_rod.gif')


@dataclass(slots=True)
class StanTraction(Exercise):
    name: str = 'Stan_traction'
    description: str = 'В чем польза: Будучи многосуставным упражнением, становая тяга укрепляет спину, ноги, ягодицы и мышцы кора, способствует развитию силы, формированию атлетического рельефа. Также становая тяга укрепляет глубокие мышцы-стабилизаторы позвоночника, формируя правильную осанку и избавляя от болей в спине.\nКак выполнять: Штангу в этом упражнении берут с пола прямым или смешанным хватом. Подойдя к снаряду на максимальное расстояние, согните ноги в коленях и наклонитесь с прямой спиной, чтобы взять штангу с пола. Плечи должны быть развернуты, подбородок приподнят. Поднимите штангу, выпрямляя ноги, но не отклоняйтесь назад. Тяните снаряд до уровня бедер, не выпрямляя колени полностью, а затем опускайте на пол, сгибая колени и наклоняясь вперед.'
    animationPath: Path = Path('exercises', 'Stan_traction.gif')


@dataclass(slots=True)
class TractionToBelt(Exercise):
    name: str = 'Traction_to_belt'
    description: str = 'В чем польза: Как базовое упражнение со штангой тяга к поясу развивает общую силу тела, прокачивая все крупные мышечные группы спины, а также укрепляет руки, плечи и грудь.\nКак выполнять: Перед выполнением упражнения положите гриф на стойку перед собой, а затем возьмите штангу прямым хватом. Согните ноги в коленях и подайтесь вперед, наклоняя спину. Приподнимите подбородок и слегка прогнитесь в спине. Теперь согните руки в локтях, притягивая штангу к поясу. Локти должны двигаться строго назад и сгибаться под прямым углом. Затем выпрямите руки, возвращаясь в начальное положение и снова повторите движение.'
    animationPath: Path = Path('exercises', 'Traction_to_belt.gif')


@dataclass(slots=True)
class Exercises(DictLikeClass):
    benchPresDumbbellsLying: BenchPressDumbbellsLying = field(default_factory=BenchPressDumbbellsLying)
    benchPresDumbbellSitting: BenchPressDumbbellsSitting = field(default_factory=BenchPressDumbbellsSitting)
    benchPressLying: BenchPressLying = field(default_factory=BenchPressLying)
    bendingHandsWithRod: BendingHandsWithRod = field(default_factory=BendingHandsWithRod)
    breedingDumbbellsLying: BreedingDumbbellsLying = field(default_factory=BreedingDumbbellsLying)
    fightingHandsTilt: FightingHandsTilt = field(default_factory=FightingHandsTilt)
    frenchBenchPressLying: FrenchBenchPressLying = field(default_factory=FrenchBenchPressLying)
    pushups: Pushups = field(default_factory=Pushups)
    squatsWithRod: SquatsWithRod = field(default_factory=SquatsWithRod)
    stanTraction: StanTraction = field(default_factory=StanTraction)
    tractionToBelt: TractionToBelt = field(default_factory=TractionToBelt)


@dataclass(slots=True)
class BotPrefs(DictLikeClass):
    exercises: Exercises = field(default_factory=Exercises)


botPrefs = BotPrefs.fromFile(Database.botPrefsFilePath)
_botPrefs = BotPrefs()


@dataclass(slots=True)
class Approaches(DictLikeClass):
    amount: int
    repetitions: int
    weight: float


@dataclass(slots=True)
class WarmUpApproaches(Approaches):
    pass


@dataclass(slots=True)
class MainApproaches(Approaches):
    pass


@dataclass(slots=True)
class UserExercise(DictLikeClass):
    name: str
    warmUpApproaches: WarmUpApproaches
    mainApproaches: MainApproaches
    note: str


@dataclass(slots=True)
class BaseUser(DictLikeClass):
    id: int = 0
    firstName: str = ''
    lastName: str = ''
    gender: int = 0
    profile: int = 0
    day: int = 0
    exercise: int = 0
    exercises: list[UserExercise] = field(default_factory=list)
    profiles: list[list[list[str]]] = field(default_factory=list)

    @property
    def exercisesNames(self):
        return {exercise.name for exercise in self.exercises}

    def getExerciseByName(self, name: str) -> UserExercise:
        return self.exercises[[*self.exercisesNames].index(name)]

    @property
    def currentExercise(self) -> UserExercise:
        return self.getExerciseByName(self.profiles[self.profile][self.day][self.exercise])


class Users(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def toDict(self) -> dict[str, Any]:
        return {userIdStr_: userClass.toDict for userIdStr_, userClass in self.items()}

    def toFile(self, file_path: Path | str = Database.usersFilePath) -> None:
        with open(file_path, 'w') as file:
            file.write(dumps(self.toDict, indent=4, escape_forward_slashes=False))

    @classmethod
    def fromDict(cls, dictionary: dict[str, Any], user_class: Type[BaseUser] = BaseUser) -> Self:
        return cls({userIdStr_: user_class.fromDict(userDict) for userIdStr_, userDict in dictionary.items()})

    @classmethod
    def fromFile(cls, file_path: Path | str = Database.usersFilePath, user_class: Type[BaseUser] = BaseUser) -> Self:
        if not exists(Database.reserveCopyFolderPath):
            makedirs(Database.reserveCopyFolderPath)
        if not exists(file_path):
            with open(file_path, 'w') as file:
                file.write('{}')
        try:
            with open(file_path) as file:
                return cls.fromDict(loads(file.read()), user_class)
        except JSONDecodeError:
            return cls()
