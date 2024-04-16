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


__all__ = ['botPrefs', 'DictLikeClass', 'BotPrefs', 'VersionInfo', 'Users', 'BaseUser', 'UserExercise']


@dataclass
class VersionInfo:
    full: str = f'1.0.0a02.00 (000000.1-0200.{datetime.now():{Constants.DateTimeForms.forVersion}})'
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
class LastVersion(DictLikeClass):
    version: str = ''
    messageId: int = 0


@dataclass(slots=True)
class Exercise(DictLikeClass):
    name: str
    description: str
    animationVkId: str


@dataclass(slots=True)
class BenchPressDumbbellsLying(Exercise):
    name: str = 'Жим гантелей лёжа'
    description: str = 'В чем польза: Представленное упражнение для мужчин в домашних условиях также относится к разряду базовых, поскольку оно крайне эффективно работает в вопросах наращивания объема груди. Жим гантелей практически ничем не отличается от жима штанги, становясь отличной альтернативой как в домашних условиях, так и в зале.\nКак выполнять: Жим производится лежа на специальной скамейке. Для начала возложите вес на грудь продольным хватом, после чего с усилием выжимайте его перед собой, не допуская закрытия локтевого замка. Опускайте гантели обратно медленно, без резких движений или бросков.'
    animationVkId: str = f'doc{Constants.devId}_674959062'


@dataclass(slots=True)
class BenchPressDumbbellsSitting(Exercise):
    name: str = 'Жим гантелей сидя'
    description: str = 'В чем польза: Тренировка для мужчин на плечи начинается с базового жима сидя. Это элемент, развивающий объем и силу дельтоидов. Это технически простое движение, не оказывающее лишней нагрузки на позвоночник. С легким весом можно работать хоть каждый день — никаких перегрузок вы не испытаете.\nКак выполнять: Для работы желательно использовать стул с высокой спинкой. Сядьте на него, выпрямите спину. Вес поднимите так, будто удерживаете гриф штанги. После этого выжимайте снаряды над головой, не допуская защелкивания локтевого замка. В процессе движения предплечья всегда перпендикулярны полу.'
    animationVkId: str = f'doc{Constants.devId}_674959186'


@dataclass(slots=True)
class BenchPressLying(Exercise):
    name: str = 'Жим лёжа'
    description: str = 'В чем польза: Упражнение развивает верхнюю часть тела, увеличивая силу рук и плеч, а также формирует рельеф в области груди. Кроме того, жим лежа способствует растягиванию грудных, что увеличивает их эластичность и потенциал к росту.\nКак выполнять: Жим лежа выполняется на прямой или наклонной скамье со стойками для грифа. Для выполнения лягте на скамью и возьмите гриф прямым закрытым хватом. Расстояние между ладонями должно быть чуть шире плеч. Опустите штангу к груди, разводя локти в стороны до параллели с полом. Затем выжмите гриф вверх, выпрямляя руки. Во время жима локти должны быть согнуты под прямым углом и смотреть в стороны, а не вниз.'
    animationVkId: str = f'doc{Constants.devId}_674959216'


@dataclass(slots=True)
class BendingHandsWithRod(Exercise):
    name: str = 'Сгибание рук со штангой'
    description: str = 'В чем польза: Сгибание рук на бицепс поможет вам увеличить руки в объеме и укрепить плечевой пояс. Кроме того, упражнение улучшает кровообращение в верхней части тела и стимулирует метаболизм.\nКак выполнять: Для выполнения возьмите штангу обратным хватом и опустите прямые руки вниз, согнув их немного в локтях. Теперь сгибайте руки с полной амплитудой, приводя штангу к груди. В нижней точке оставляйте локти немного согнутыми, что поможет предотвратить травмы. Выполняйте упражнение медленно без резких движений, сосредоточившись на напряжении бицепсов рук.'
    animationVkId: str = f'doc{Constants.devId}_674959243'


@dataclass(slots=True)
class BreedingDumbbellsLying(Exercise):
    name: str = 'Разведение гантелей лёжа'
    description: str = 'В чем польза: Целевой группой при работе являются большие грудные мышцы. Они практически полностью изолируются в процессе работы. Поскольку бицепс и трицепс помогает удерживать гантели в определенном положении, на них тоже приходится определенная часть нагрузки. Ягодицы, живот и мелкие мышцы корпуса удерживают тело неподвижно.\nКак выполнять: Разводите вес до уровня, пока не почувствуете приличное натяжение в области груди. Не нужно перебарщивать, опуская снаряды до боли в плечах — это опасно. Разведение выполняется в среднем темпе без резких рывков. Руки всегда держите в слегка согнутом положении.'
    animationVkId: str = f'doc{Constants.devId}_674959267'


@dataclass(slots=True)
class FightingHandsTilt(Exercise):
    name: str = 'Разгибание рук в наклоне'
    description: str = 'В чем польза: В качестве агонистов выступают локтевые мышцы и трицепсы. В качестве стабилизаторов используются задние пучки дельт, а также разгибатели плеча. Статической нагрузке поддается поясничная группа мышц. Упражнение идеально подходит и новичкам, и профессионалам.\nКак выполнять: Упражнение, входящее в программу для мужчин на неделю, делается в наклоне. Соблюдайте небольшой полуприсед. Руки необходимо держать прижатыми к бокам корпуса. Разгибайте верхние конечности до уровня, пока они не образуют прямую линию. Напряжение при этом сосредотачивается в трицепсах.'
    animationVkId: str = f'doc{Constants.devId}_674959301'


@dataclass(slots=True)
class FrenchBenchPressLying(Exercise):
    name: str = 'Французский жим лёжа'
    description: str = 'В чем польза: Французский жим способствует набору массы в верхней части рук, формируя внушительный рельеф. Также упражнение укрепляет суставы, улучшая их подвижность и стабилизируя их за счет роста мышц.\nКак выполнять: Чтобы выполнить упражнение, возьмите гриф прямым хватом и лягте на прямую скамью без стоек. Поднимите штангу над собой и согните руки в локтях, опуская гриф за голову. Не сгибайте локти более чем на 90 градусов, чтобы не травмировать плечи. Выполняйте упражнение осторожно в медленном темпе, акцентируя внимание на работе задней части рук. Для упражнения подойдет не только прямой, но и Z-гриф.'
    animationVkId: str = f'doc{Constants.devId}_674959332'


@dataclass(slots=True)
class Pushups(Exercise):
    name: str = 'Отжимания'
    description: str = 'В чем польза: Это базовое упражнение для дома, являющееся одним из самых популярных среди упражнений с весом собственного тела. Оно эффективно развивает объемы и силу груди и трицепсов, являясь при этом минимально травмоопасным упражнением.\nКак выполнять: Примите классический упор лежа, расположив ладони немного шире уровня ключиц. Отжимание выполняйте до уровня, пока грудь не окажется в 2-3 см от пола. Локти старайтесь прижимать к бокам и направлять назад.'
    animationVkId: str = f'doc{Constants.devId}_674959352'


@dataclass(slots=True)
class SquatsWithRod(Exercise):
    name: str = 'Приседания со штангой'
    description: str = 'В чем польза: Приседания с весом укрепляют мышцы кора и нижней части тела, а также суставно-связочный аппарат, увеличивают силу и выносливость организма, улучшают баланс и координацию движений, формируют красивый рельеф ног и ягодиц.\nКак выполнять: Если вы тренируетесь в зале, то это упражнение со штангой лучше выполнять в силовой раме. Положите гриф на область трапеций. Упритесь пятками в пол и начинайте приседание. Подбородок приподнят, плечи развернуты, спина прямая. Отводите таз максимально назад, не сгибаясь в пояснице. Приседайте до параллели с полом, следите, чтобы носки находились на уровне коленей. Не подворачивайте таз при подъеме и держите колени немного согнутыми, чтобы снизить на них нагрузку.'
    animationVkId: str = f'doc{Constants.devId}_674959369'


@dataclass(slots=True)
class StanTraction(Exercise):
    name: str = 'Становая тяга'
    description: str = 'В чем польза: Будучи многосуставным упражнением, становая тяга укрепляет спину, ноги, ягодицы и мышцы кора, способствует развитию силы, формированию атлетического рельефа. Также становая тяга укрепляет глубокие мышцы-стабилизаторы позвоночника, формируя правильную осанку и избавляя от болей в спине.\nКак выполнять: Штангу в этом упражнении берут с пола прямым или смешанным хватом. Подойдя к снаряду на максимальное расстояние, согните ноги в коленях и наклонитесь с прямой спиной, чтобы взять штангу с пола. Плечи должны быть развернуты, подбородок приподнят. Поднимите штангу, выпрямляя ноги, но не отклоняйтесь назад. Тяните снаряд до уровня бедер, не выпрямляя колени полностью, а затем опускайте на пол, сгибая колени и наклоняясь вперед.'
    animationVkId: str = f'doc{Constants.devId}_674959390'


@dataclass(slots=True)
class TractionToBelt(Exercise):
    name: str = 'Тяга к поясу'
    description: str = 'В чем польза: Как базовое упражнение со штангой тяга к поясу развивает общую силу тела, прокачивая все крупные мышечные группы спины, а также укрепляет руки, плечи и грудь.\nКак выполнять: Перед выполнением упражнения положите гриф на стойку перед собой, а затем возьмите штангу прямым хватом. Согните ноги в коленях и подайтесь вперед, наклоняя спину. Приподнимите подбородок и слегка прогнитесь в спине. Теперь согните руки в локтях, притягивая штангу к поясу. Локти должны двигаться строго назад и сгибаться под прямым углом. Затем выпрямите руки, возвращаясь в начальное положение и снова повторите движение.'
    animationVkId: str = f'doc{Constants.devId}_674959400'


@dataclass(slots=True)
class Exercises(DictLikeClass):
    benchPressDumbbellsLying: BenchPressDumbbellsLying = field(default_factory=BenchPressDumbbellsLying)
    benchPressDumbbellSitting: BenchPressDumbbellsSitting = field(default_factory=BenchPressDumbbellsSitting)
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
    lastVersion: LastVersion = field(default_factory=LastVersion)
    apiVersion: str = '5.131'
    exercises: Exercises = field(default_factory=Exercises)
    devId: int = Constants.devId
    admins: list[int] = field(default_factory=lambda: [Constants.devId])
    sendExecutionTime: bool = True

    @property
    def exercisesNames(self) -> list[str]:
        return [exerciseName for exerciseName, _ in self.exercises]

    @property
    def exercisesNamesRu(self) -> list[str]:
        return [exercise.name for _, exercise in self.exercises]

    def getExerciseByNameRu(self, name: str) -> Exercise:
        return self.exercises.values[self.exercisesNamesRu.index(name)]


botPrefs = BotPrefs.fromFile(Database.botPrefsFilePath)
_botPrefs = BotPrefs()


@dataclass(slots=True)
class Approaches(DictLikeClass):
    amount: int = 0
    repetitions: int = 0
    weight: float = 0


@dataclass(slots=True)
class WarmUpApproaches(Approaches):
    pass


@dataclass(slots=True)
class MainApproaches(Approaches):
    pass


@dataclass(slots=True)
class UserExercise(DictLikeClass):
    name: str = ''
    warmUpApproaches: WarmUpApproaches = field(default_factory=WarmUpApproaches)
    mainApproaches: MainApproaches = field(default_factory=MainApproaches)
    note: str = ''


@dataclass(slots=True)
class BaseUser(DictLikeClass):
    id: int = 0
    firstName: str = ''
    lastName: str = ''
    gender: int = 0
    profile: int = 0
    day: int = 0
    exercise: int = 0
    exerciseEditing: int = 0
    exercises: list[UserExercise] = field(default_factory=lambda: [UserExercise(exerciseName) for exerciseName in botPrefs.exercisesNamesRu])
    profiles: list[list[list[str]]] = field(default_factory=list)
    profileNames: list[str] = field(default_factory=list)
    lastMessage: str = ''
    lastKeyboard: str = 'main'

    @property
    def fullName(self) -> str:
        return f'{self.firstName} {self.lastName}'

    @property
    def exercisesNames(self) -> list[str]:
        return [exercise.name for exercise in self.exercises]

    def getExerciseByName(self, name: str) -> UserExercise:
        return self.exercises[[*self.exercisesNames].index(name)]

    @property
    def currentProfileName(self) -> str:
        return self.profileNames[self.profile]

    @property
    def currentProfile(self) -> list[list[str]]:
        return self.profiles[self.profile] if self.profile < len(self.profiles) else []

    @property
    def currentDay(self) -> list[str]:
        return self.profiles[self.profile][self.day] if self.day < len(self.profiles[self.profile]) else []

    @property
    def currentExercise(self) -> UserExercise:
        return self.getExerciseByName(self.profiles[self.profile][self.day][self.exercise])

    def createKeyboard(self, keyboard_type: str, inline: bool = None, has_to_menu_button: bool = None) -> str:
        inline = keyboard_type in Constants.inlineKeyboards if inline is None else inline
        hasToMenuButton = keyboard_type in Constants.keyboardsWithToMenuButton if has_to_menu_button is None else has_to_menu_button
        if keyboard_type == 'last':
            keyboard_type = self.lastKeyboard
        kb = VkKeyboard(inline=inline)

        match keyboard_type:

            case 'main':
                kb.add_button('Профили', 'primary')
                kb.add_button('Упражнения', 'secondary')

            case 'profiles':
                kb.add_button('Создать новый профиль', 'primary')
                for profile in self.profileNames:
                    kb.add_line()
                    kb.add_button(profile, 'positive')
                kb.add_line()
                kb.add_button('Назад', 'negative')

            case 'days':
                kb.add_button('Добавить день', 'primary')
                for day in range(len(self.currentProfile)):
                    if day % 2:
                        kb.add_line()
                    kb.add_button(f'День {day + 1}', 'positive')
                kb.add_line()
                kb.add_button('Назад', 'negative')

            case 'exercises':
                kb.add_button('Удалить день', 'negative')
                kb.add_line()
                kb.add_button('Добавить упражнение', 'primary')
                for exercise in self.currentDay:
                    kb.add_line()
                    kb.add_button(exercise, 'positive')
                kb.add_line()
                kb.add_button('Назад', 'negative')

            case 'exercise_list' | 'add_exercise':
                for counter, (_, exercise) in enumerate(botPrefs.exercises):
                    kb.add_button(exercise.name, 'positive')
                    if counter % 2:
                        kb.add_line()
                kb.add_line()
                kb.add_button('Назад', 'negative')

            case 'profile_actions':
                kb.add_button('Войти', 'primary')
                kb.add_line()
                kb.add_button('Переименовать', 'positive')
                kb.add_line()
                kb.add_button('Удалить', 'negative')

            case 'exercise_actions':
                kb.add_button(f'[Р] Подходы', 'negative')
                kb.add_button(f'[О] Подходы', 'positive')
                kb.add_line()
                kb.add_button(f'[Р] Повторения', 'negative')
                kb.add_button(f'[О] Повторения', 'positive')
                kb.add_line()
                kb.add_button(f'[Р] Вес', 'negative')
                kb.add_button(f'[О] Вес', 'positive')
                kb.add_line()
                kb.add_button('Заметка', 'secondary')

            case 'exercise_actions_extended':
                kb.add_button(f'[Р] Подходы', 'negative')
                kb.add_button(f'[О] Подходы', 'positive')
                kb.add_line()
                kb.add_button(f'[Р] Повторения', 'negative')
                kb.add_button(f'[О] Повторения', 'positive')
                kb.add_line()
                kb.add_button(f'[Р] Вес', 'negative')
                kb.add_button(f'[О] Вес', 'positive')
                kb.add_line()
                kb.add_button('Заметка', 'secondary')
                kb.add_button('Удалить', 'negative', ['remove_exercise'])

            case _:
                return kb.get_empty_keyboard()

        if not inline and hasToMenuButton:
            kb.add_button('🔚В меню', 'negative')

        return kb.get_keyboard()


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
