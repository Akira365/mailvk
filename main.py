import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import  VkKeyboard, VkKeyboardColor
import sqlite3
import threading
import time

conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

try:
    cursor.execute('CREATE TABLE users (id int)')
    conn.commit()
except sqlite3.OperationalError:
    pass


token = 'ВАШ ТОКЕН'
group_id = 'ID ВАШЕЙ ГРУППЫ'
link = 'ССЫЛКА НА СТРИМ, КАНАЛ ИЛИ ЧТО-ТО'
# КТО МОЖЕТ ДЕЛАТЬ РАССЫЛКУ
role = ['creator', 'admin']
# НА КАКИЕ СООБЩЕНИЯ ОН БУДЕТ ЛЮДЕЙ ПОДПИСЫВАТЬ НА РАССЫЛКУ
sub = ['подписаться', '+']
# НА КАКИЕ СООБЩЕНИЯ ОН БУДЕТ ЛЮДЕЙ ОТПИСЫВАТЬ ОТ РАССЫЛКИ
unsub = ['отписаться', '-']

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def spam_bot(name, user_id):
    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                response = event.text.lower()
                if event.to_me:
                    if event.user_id == user_id:
                        msg = event.text + '\n' + link
                        cursor.execute('SELECT id FROM users')
                        users = cursor.fetchall()
                        for usr in users:
                            try:
                                vk_session.method('messages.send', {'user_id': usr, 'random_id': 0,'message': msg})
                                time.sleep(0.5)
                            except:
                                pass
                        vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0, 'message': 'Рассылка завершена.'})
                        return 0

def main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.get_empty_keyboard()
    keyboard.add_button('Рассылка', VkKeyboardColor.PRIMARY)
    keyboard = keyboard.get_keyboard()
    return keyboard

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
                response = event.text.lower()
                if event.to_me:
                    if response in sub:
                        cursor.execute(f'SELECT id FROM users WHERE id = {event.user_id}')
                        id = cursor.fetchall()
                        if str(id) == '[]':
                            cursor.execute(f'INSERT INTO users (id) VALUES ({event.user_id})')
                            conn.commit()
                            vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0,'message': 'Вы подписались на рассылку.'})
                        else:
                            vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0,'message': 'Вы уже подписаны на рассылку.'})
                    if response in unsub:
                        cursor.execute(f'SELECT id FROM users WHERE id = {event.user_id}')
                        id = cursor.fetchall()
                        if str(id) == '[]':
                            vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0,'message': 'Вы уже отписались от рассылки.'})
                            continue
                        else:
                            cursor.execute(f'DELETE FROM users WHERE id = {event.user_id}')
                            conn.commit()
                        vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0,'message': 'Вы отписались от рассылки.'})
                    usersadmin = vk_session.method('groups.getMembers', {'group_id': group_id, 'filter': 'managers'})['items']
                    for user in usersadmin:
                        if event.user_id == int(user['id']) and user['role'] in role:
                            if response == 'начать':
                                key = main_keyboard()
                                vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0, 'message': 'Вы получили права админа', 'keyboard':key})
                            if response == 'рассылка':
                                vk_session.method('messages.send', {'user_id': event.user_id, 'random_id': 0, 'message': 'Введите сообщение для рассылки (ссылку указывать не надо, вы её указывали в программе)'})
                                rT = threading.Thread(target=spam_bot, args=('spam', event.user_id))
                                rT.run()