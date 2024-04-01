from datetime import datetime
from secrets import randbelow
from socket import gethostbyname, gethostname, create_connection
from threading import Thread
from typing import Any, Iterable


from emoji import replace_emoji
from pymorphy3 import MorphAnalyzer
from rich import print as richPrint


from .config import *
from libs.vk_api_fast.bot_longpoll import VkBotEvent


__all__ = ['threadsStartJoin', 'tryParse', 'prettyRoundFloat', 'boolConverter',
           'return0s', 'randint', 'random', 'generateTimeAgo', 'matchNumber', 'constructMessageEvent',
           'getMyIP', 'isConnected', 'log']
morph = MorphAnalyzer()


def threadsStartJoin(threads: Iterable[Thread]) -> None:
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def tryParse(value: Any, parse_to: str | type) -> bool:
    try:
        eval(f'{parse_to if isinstance(parse_to, str) else parse_to.__name__}({value!r})')
        return True
    except Exception:
        return False


def prettyRoundFloat(number: float | int | str, decimal_places: int = 0) -> int | float:
    return (prettyRoundFloat(float(number), decimal_places)
            if isinstance(number, str) else
            number
            if isinstance(number, int) else
            int(number)
            if number.is_integer() else
            round(number, decimal_places))


def boolConverter(string: str) -> bool:
    if string not in {'True', 'False'}:
        raise ValueError('Invalid string to convert to boolean!')
    return True if string == 'True' else False


def return0s(number: str, keep_str: bool = False) -> float | int | str:
    numberStr = number.lower().replace('k', '000')
    return (str if keep_str else int if numberStr.isdecimal() else float)(numberStr)


def randint(lower_bound: int, upper_bound: int, step: int = 1) -> int:
    return (result := randbelow(upper_bound - lower_bound + 1) + lower_bound) - result % step


def random(precision: int = 9) -> float:
    return randbelow(10 ** precision) / 10 ** precision


def generateTimeAgo(time_ago: str, inflects: Iterable = ('nomn', 'sing')) -> str:
    timeAgo = datetime.now() - datetime.strptime(time_ago, Constants.DateTimeForms.full)
    daysAgo = timeAgo.days
    if yearsAgo := int(daysAgo // 365.2425):
        return matchNumber('год', yearsAgo, inflects)
    if monthsAgo := int(daysAgo // 30.436875):
        return matchNumber('месяц', monthsAgo, inflects)
    if weeksAgo := daysAgo // 7:
        return matchNumber('неделя', weeksAgo, inflects)
    if daysAgo:
        return matchNumber('день', daysAgo, inflects)
    secondsAgo = timeAgo.seconds
    if hoursAgo := secondsAgo // 3600:
        return matchNumber('час', hoursAgo, inflects)
    if minutesAgo := secondsAgo // 60:
        return matchNumber('минута', minutesAgo, inflects)
    return matchNumber('секунда', secondsAgo, inflects)


def matchNumber(word: str, number: int, inflects: Iterable = ('nomn', 'sing')) -> str:
    return f'{number:_} {f'{word} + {'a' if number % 10 in {2, 3, 4} and number not in {12, 13, 14} else ''}' if word == 'раз'
                         else morph.parse(word)[0].inflect({*inflects}).make_agree_with_number(number).word}'


def constructMessageEvent(group_id: int, dev_id: int, message: str) -> VkBotEvent:
    return VkBotEvent({
        'group_id': group_id, 'type': 'message_new', 'event_id': '', 'v': '5.131', 'object': {
            'message': {
                'entity_version': 0, 'date': 0, 'from_id': dev_id, 'id': 0, 'out': 0, 'attachments': [],
                'conversation_message_id': 0, 'fwd_messages': [], 'important': False, 'is_hidden': False,
                'peer_id': dev_id, 'random_id': 0, 'text': message
            },
            'client_info': {
                'button_actions': ['text', 'intent_subscribe', 'intent_unsubscribe'], 'keyboard': False, 'inline_keyboard': False,
                'carousel': False, 'lang_id': 0
            }
        }
    })


def getMyIP() -> str:
    return gethostbyname(gethostname())


def isConnected(host_name: str = Constants.vkIP) -> bool:
    try:
        create_connection((gethostbyname(host_name), 80), 2).close()
        return True
    except Exception:
        return False


def log(level: str = '', message: Any = '', importance_level: int = 0, no_level_color: str = '#ffffff',
        log_format: str = '[%level] %datetime: %message',
        datetime_format: str = Constants.DateTimeForms.forLog,
        async_: bool = True, end: str = '\n') -> None:
    """
    Pretty logging basically
    """
    if importance_level > LOG_MODE:
        return
    message = str(message)

    def log() -> None:
        match level:
            case 'info':
                color = '#00ff00'
            case 'warn':
                color = '#ffff00'
            case 'error':
                color = '#ff0000'
            case 'debug':
                color = '#ff00ff'
            case _:
                color = no_level_color
        toLog = (log_format
                 .replace('%level', level.upper())
                 .replace('%datetime', f'{datetime.now():{datetime_format}}')
                 .replace('%message', message))
        logs.append(toLog)
        try:
            richPrint(f'[{color}]{toLog}[/{color}]', end=end)
        except UnicodeEncodeError:
            try:
                richPrint(f'[{color}]{replace_emoji(toLog)}[/{color}]', end=end)
            except UnicodeEncodeError:
                print(f'{toLog!a}', end=end)
    if async_:
        Thread(target=log, name='Logger').start()
    else:
        log()
