from ctypes import windll
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from itertools import batched
from math import inf, prod
from os import listdir, remove as rmfile
from pathlib import Path
from secrets import choice as select
from shutil import get_terminal_size
from sys import exit
from threading import Thread
from time import perf_counter, sleep
from traceback import format_exc
from typing import Any, Literal

from requests.exceptions import ConnectTimeout
from tendo.singleton import SingleInstance, SingleInstanceException
from ujson import dumps, loads

from .config import *
from .classes import *
from .functions import *
from libs.vk_api_fast import VkApi
from libs.vk_api_fast.bot_longpoll import VkBotEvent, VkBotEventType, VkBotLongPoll
from libs.vk_api_fast.exceptions import ApiError, VkApiError


botPrefs: BotPrefs


def main():
    versionInfo, timerStart = VersionInfo(), perf_counter()

    @dataclass(slots=True)
    class User(BaseUser):
        def sendMessage(self,
                        keyboard: str = 'last', message: Any = None,
                        attachments: Any = None, time: float = 0.,
                        max_message_length: int = 4096) -> None:
            if not message:
                return
            message = str(message).strip('\n').replace('\'', '"')
            if self.id in {*botPrefs.admins} and botPrefs.sendExecutionTime:
                message += f'\n\nВыполнено за {time:.6f} секунд'
            try:
                keyboard = self.createKeyboard(keyboard)
                for messagePart in batched(message, max_message_length):
                    Thread(
                        target=vkApi.messages.send,
                        kwargs={
                            'user_id': self.id,
                            'message': ''.join(messagePart),
                            'keyboard': keyboard,
                            'random_id': 0,
                            'attachments': ''
                        },
                        name='Message sender'
                    ).start()
                log('info',
                    f'Bot\'s response to {self.getName(name_form='full', with_id=True)}:\n'
                    f'{message if message else '*No response*'}{f'\nExecuted in {time:.6f} second(s)' if time else ''}', 1)
            except ApiError:
                log('error',
                    f'Unable to send message to user '
                    f'{self.getName(name_form='full', with_id=True)} without their permission.')

        def getName(self, *,
                    name_form: Literal['full', 'short'] = 'short',
                    name_case: Literal['nom', 'gen', 'dat', 'acc', 'ins', 'abl'] = 'nom',
                    with_id: bool = False) -> str:
            if name_case != 'nom':
                try:
                    userInfo = vkApi.users.get(user_ids=(self.id,), name_case=name_case)[0]
                except Exception:
                    userInfo = {'first_name': self.firstName, 'last_name': self.lastName}
                result = (f'{userInfo['first_name']} {userInfo['last_name']}'
                          if name_form == 'full' else userInfo['first_name'])
            else:
                result = self.fullName if name_form == 'full' else self.firstName
            if with_id:
                result += f' (id: {self.id})'
            return result

    users: Users[str, User] = Users.fromFile(user_class=User)

    vk = VkApi(token=group.tokenGroup, api_version=botPrefs.apiVersion)
    vkApi = vk.get_api()
    if None in {group.title, group.name}:
        groupInfo = vkApi.groups.getById(group_id=group.id)[0]
        if group.title is None:
            group.title = groupInfo['name']
        if group.name is None:
            group.name = groupInfo['screen_name']

    log(no_level_color='#00ffff', log_format='%message', async_=False,
        message=f'{f' {group.title} v{versionInfo.full.split()[0]}: {versionInfo.name} ':=^{get_terminal_size().columns - get_terminal_size().columns % 2 - 1}}')
    log('info', 'Starting bot...')

    longpoll = VkBotLongPoll(vk, group.id)
    vkUserApi = VkApi(token=group.tokenUser, api_version=botPrefs.apiVersion).get_api()
    log('info', 'Logged to VK')

    def onEvent(vk_event: VkBotEvent) -> None:
        def onMessage() -> None:
            nonlocal response, responseDefault, responseAdditional, message, kb
            if userId in {*botPrefs.admins} and response[0] == '.':
                cmdMsg: list[bool | float | int | str] = responseDefault.split(' ')
                cmdSyntax = cmds[0] if (cmds := [command for command in Constants.commands.splitlines() if cmdMsg[0] in command]) else ''
            if not WORKING and userId not in {*botPrefs.admins}:
                message = '❕Бот временно выключен.'
                return
            match response:
                case 'start' | 'начать':
                    kb = 'main'
                    message = 'Привет'
                case 'создать новый профиль':
                    message = 'Введите имя нового профиля.'
                case 'переименовать':
                    message = f'Введите новое название профиля {user.currentProfileName!r}.'
                case 'удалить':
                    del user.profiles[user.profile], user.profileNames[user.profile]
                    user.profile = 0
                    message = f'Профиль {user.currentProfileName!r} удалён.'
                case _:
                    if responseDefault in {*user.profileNames}:
                        kb = 'edit_profile'
                        user.profile = user.profileNames.index(responseDefault)
                        message = f'Выберите действие с профилем {responseDefault!r}.'
                    match user.lastMessage:
                        case 'Создать новый профиль':
                            if responseDefault in {*user.profileNames}:
                                message = 'Профиль с таким именем уже существует.'
                                return
                            user.profiles.append([])
                            user.profileNames.append(responseDefault)
                            message = f'Новый профиль {responseDefault!r} добавлен.'
                        case 'Переименовать':
                            if responseDefault in {*user.profileNames}:
                                message = 'Профиль с таким именем уже есть!'
                                return
                            user.profileNames[user.profile] = responseDefault

        try:
            log('info', f'New event: {str(vk_event.type).split('.')[1].replace('_', ' ').lower()}')
        except IndexError:
            log('info', f'New event: {str(vk_event.type).replace('_', ' ').lower()}')

        userId, message, responseDefault, responseAdditional, kb, timerStart = 0, '', '', '', 'last', perf_counter()
        match vk_event.type:
            case VkBotEventType.MESSAGE_NEW:
                payload = loads(vk_event.object.message['payload']) if 'payload' in {*vk_event.object.message} else vk_event.object.message['text']
                userId, responseDefault = vk_event.object.message['from_id'], (
                    payload[0] if isinstance(payload, list) else
                    payload['command'] if isinstance(payload, dict) else payload
                )
                if isinstance(payload, list):
                    if len(payload) > 1:
                        responseAdditional = payload[1]
        if userId < 0:
            return
        if (userIdStr := str(userId)) not in {*users}:
            addUser(userId)
        user = users[userIdStr]

        try:
            match vk_event.type:
                case VkBotEventType.MESSAGE_NEW | VkBotEventType.MESSAGE_EDIT:
                    response = responseDefault.lower()
                    if not response or response[0] == ',':
                        return
                    log('info', f'{user.getName(name_form='full', with_id=True)} '
                                f'messaged:\n{responseDefault}', 1)
                    onMessage()
                    if not message:
                        message = ('❗Вы ввели неизвестную команду. '
                                   'Если у вас пропала клавиатура бота, нажмите кнопку для её открытия справа от поля ввода сообщения или напишите "Начать".')
                    user.lastMessage = responseDefault
            if kb != 'last' and kb not in Constants.inlineKeyboards:
                user.lastKeyboard = kb
            timerEnd = perf_counter()
            user.sendMessage(kb, message, timerEnd - timerStart)
            users[userIdStr] = user

        except Exception:
            user.sendMessage(
                'sendBugReport',
                f'❗В работе бота произошла непредвиденная ошибка при обработке сообщения, и сообщение с отчётом об ошибке было отправлено разработчику. '
                f'Надеемся, такого больше не повторится.',
                0)
            users[str(botPrefs.devId)].sendMessage(message=f'{format_exc()}User: {user.getName(with_id=True)}')

    def postUpdateMessage() -> None:
        def postUpdateMessage() -> None:
            try:
                botPrefs.lastVersion.messageId = 0
                postCount = vkUserApi.wall.get(owner_id=-group.id)['count']
                postOffsets = [*range(postCount - 100, postCount % 100 - 1, -100)] + [0]
                for postOffset in postOffsets:
                    for post in vkUserApi.wall.get(owner_id=-group.id, count=100, offset=postOffset)['items']:
                        if 'Обновление' in post['text']:
                            botPrefs.lastVersion.messageId = post['id']
                            break
                    else:
                        continue
                    break
                assert botPrefs.lastVersion.messageId, 'Couldn\'t get update message post id!'
                vkUserApi.wall.edit(owner_id=-group.id, post_id=botPrefs.lastVersion.messageId, signed=0,
                                    message=f'🔥Обновление {versionInfo.full}: {versionInfo.name}!🔥'
                                            f'\n\n📃Список изменений в версии {versionInfo.main}:{versionInfo.changelog}')
                log('info', 'Edited update message')
            except (ApiError, AssertionError) as exception:
                try:
                    if botPrefs.lastVersion.messageId:
                        log('warn', f'Couldn\'t edit update message! Cause:\n{exception}')
                        vkUserApi.wall.delete(owner_id=-group.id, post_id=botPrefs.lastVersion.messageId)
                        log('info', 'Deleted old update message')
                    vkUserApi.wall.post(owner_id=-group.id, from_group=1,
                                        message=f'🔥Обновление {versionInfo.full}: {versionInfo.name}!🔥'
                                                f'\n\n📃Список изменений в версии {versionInfo.main}:{versionInfo.changelog}')
                    log('info', 'New update message posted!')
                except ApiError as exception:
                    log('warn', f'Couldn\'t delete/post update message! Cause:\n{exception}\n')

            botPrefs.lastVersion.version = versionInfo.full

        Thread(target=postUpdateMessage, name='Update message handler').start()

    def addUser(user_id: int) -> None:
        if (user_id_str := str(user_id)) not in {*users}:
            users.update({user_id_str: User(id=user_id)})

        log('info', f'Added user {users[user_id_str].getName(with_id=True)}', 2)

    def updateBotStatus(status: bool = True, async_: bool = True) -> None:
        def updateBotStatus() -> None:
            try:
                if status:
                    newDescription = (f'Бот работает {'стабильно.' if versionInfo.full.split()[0][-1] == 'r' else
                                                      'в тестовом режиме. Могут возникать ошибки.'}' if WORKING else
                                      'Бот выключен и доступен только для админов.')
                    switchOnlineStatus = vkApi.groups.enableOnline
                else:
                    newDescription = 'Бот временно выключен.'
                    switchOnlineStatus = vkApi.groups.disableOnline
                descriptionEditThread = Thread(target=vkApi.groups.edit,
                                               kwargs={'group_id': group.id, 'description': newDescription},
                                               name='Description editer')
                descriptionEditThread.start()
                switchOnlineStatus(group_id=group.id)
                descriptionEditThread.join()
            except ApiError as exception:
                log('warn', f'Couldn\'t change bot status. Cause:\n{exception}')
            log('info', f'Updated bot status to O{'N' if status else 'FF'}')
        decideAsync(async_, updateBotStatus, 'Bot status updater')

    def updateAtJSON(one_time: bool = True, async_: bool = True, delaySeconds: int = 60) -> None:
        def updateAtJSON():
            try:
                updateReserveCopyThread = Thread(target=updateReserveCopy, args=(one_time, async_), name='Reserve copy updater')
                updateReserveCopyThread.start()
                if not one_time:
                    updateReserveCopyThread.join()
                while True:
                    try:
                        users.toFile()
                        botPrefs.toFile(Database.botPrefsFilePath)
                        log('info', 'Saved database files')
                        if one_time:
                            break
                        sleep(delaySeconds)
                    except Exception:
                        log('error', 'Unable to save JSON files')
                updateReserveCopyThread.join()
            except Exception:
                log('error', 'Unable to save JSON files')
        decideAsync(async_, updateAtJSON, 'JSON updater')

    def updateReserveCopy(one_time: bool = True, async_: bool = True, delaySeconds: int = 3600) -> None:
        def updateReserveCopy():
            while True:
                try:
                    users.toFile(Path(Database.reserveCopyFolderPath,
                                      f'{datetime.now():{Constants.DateTimeForms.forReserveCopy}}_{Database.usersFileName}'))
                    for file in listdir(str(Database.reserveCopyFolderPath)):
                        if (file.endswith('.json') and
                            (datetime.now() - datetime.strptime('_'.join(file.split('_')[:2]), Constants.DateTimeForms.forReserveCopy)).days >
                            Database.reserveCopyDeleteTimeDays):
                            rmfile(Path(Database.reserveCopyFolderPath, file))
                    log('info', 'Saved database reserve copy')
                    if one_time:
                        break
                    sleep(delaySeconds)
                except Exception:
                    log('error', 'Unable to save reserve copy')
        decideAsync(async_, updateReserveCopy, 'Reserve copy updater')

    def respondToUnreadMessages() -> None:
        def respondToUnreadMessages() -> None:
            unreadConversations = vkApi.messages.getConversations(group_id=group.id, filter='unread')['items']
            for unreadConversation in unreadConversations:
                if (unreadUserIdStr := str(unreadUserId := unreadConversation['conversation']['peer']['id'])) not in {*users}:
                    addUser(unreadUserId)
                users[unreadUserIdStr].sendMessage(message='❕Когда вы написали боту в последний раз, он был выключен и не отвечал на ваши сообщения.'
                                                           'Теперь он снова работает.')
            if unreadConversations:
                log('info', 'Unread messages were answered')
        Thread(target=respondToUnreadMessages, name='Unread messages answerer').start()

    respondToUnreadMessages()
    if not SKIP_UPDATES:
        if group.tokenUser and botPrefs.lastVersion.version != versionInfo.full and POST_UPDATE_MESSAGE:
            postUpdateMessage()
        updateBotStatus()
    updateAtJSON(False)

    timerEnd = perf_counter()
    log('info', f'Started bot at https://vk.me/{group.name} in {timerEnd - timerStart:.6f} seconds')

    try:
        while True:
            try:
                for vk_event in longpoll.listen():
                    Thread(target=onEvent, args=(vk_event,), name='Event handler').start()
            except Exception as exception:
                while not isConnected():
                    pass
                users[str(botPrefs.devId)].sendMessage(message=f'❗Произошла ошибка:\n{exception}')
                log('error', str(exception))
    finally:
        log('info', 'Exiting...')
        updateAtJSON(async_=False)
        updateBotStatus(False, False)
        log('info', 'Exited successfully. Now you can close this window.')
        exit()


def preMain() -> None:
    try:
        me = SingleInstance()
    except SingleInstanceException:
        windll.user32.MessageBoxW(0, 'Another instance of the bot is already running!', 'Error!', 0, 0x00001000)
        exit()
    if not isConnected():
        windll.user32.MessageBoxW(0, 'No Internet connection!', 'Error!', 0, 0x00001000)
        exit()
    while True:
        try:
            main()
        except Exception as exception:
            log('error', exception)
            log('info', 'Critical error occurred, restarting bot...')


if __name__ == '__main__':
    preMain()
