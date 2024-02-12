import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import datetime
import requests
from urllib.error import HTTPError
import pymorphy2

TOKEN = "7921ac48e001ac284a2e202d229a7fe2607995dd25"\
    "f8585d0155ae1715780339540348a8bdc4742d831e5"
API = "1779c165ad1cb592262d0b342ac9afba"
ID_ = 203064411
vk_session = vk_api.VkApi(token=TOKEN)
flag = 0


def weather(city_name, A, zapr):
    emj = {"пасмурно": "☁", "небольшой дождь": "🌧", "ясно": "☀", 
           "небольшой снег": "🌨", "облачно с прояснениями": "⛅",
           "дождь": "🌧", "переменная облачность": "☁", "снег": "🌨",
           "небольшая облачность": "🌥"}
    try:
        response = \
            requests.get("http://api.openweathermap.org/data/2.5/forecast",
                         params={'q': city_name, 'type': 'like', 
                                 'units': 'metric', 'lang': 'ru', 
                                 'APPID': API})
    except HTTPError:
        return False
    else:
        data = response.json()
        try:
            a = data["list"]
        except IndexError:
            return False
        else:
            MESSAGE = "время___темпер.___состояние\n"
            if "завтра" in zapr:
                for i in data['list']:
                    today = datetime.date.today()
                    tomorrow = today + datetime.timedelta(days=1)
                    ll = tomorrow.strftime('%Y-%m-%d')
                    if i['dt_txt'].split()[0] == ll:
                        a = i['dt_txt'].split()[1], \
                            '{0:+3.0f}'.format(i['main']['temp']), \
                            i['weather'][0]['description']
                        MESSAGE += "\n" + str(a[0]) + "___" + str(a[1]) + \
                            "___" + str(a[2]) + emj[str(a[2])] + "\n"
            elif "сегодня" in zapr:
                for i in data['list']:
                    if i['dt_txt'].split()[0] == \
                       str(datetime.datetime.now()).split()[0]:
                        a = i['dt_txt'].split()[1], \
                            '{0:+3.0f}'.format(i['main']['temp']), \
                            i['weather'][0]['description']
                        MESSAGE += "\n" + str(a[0]) + "___" + str(a[1]) + \
                            "___" + str(a[2]) + emj[str(a[2])] + "\n"
            else:
                for i in data['list']:
                    if i['dt_txt'].split()[0] == \
                       str(datetime.datetime.now()).split()[0]:
                        a = i['dt_txt'].split()[1], \
                            '{0:+3.0f}'.format(i['main']['temp']),\
                            i['weather'][0]['description']
                        MESSAGE += "\n" + str(a[0]) + "___" + str(a[1]) + \
                            "___" + str(a[2]) + emj[str(a[2])] + "\n"
            return MESSAGE


def choose_city():
    morph = pymorphy2.MorphAnalyzer()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_chat:
                for elem in event.text.lower().split():
                    word = morph.parse(elem)[0]
                    if 'NOUN' in word.tag.POS:
                        word = word.inflect({'nomn'}).word
                    else:
                        word = elem
                    with open("ru.txt", "r") as names:
                        names = names.read().split("\n")
                        if word.capitalize() in names:
                            return word
                        else:
                            return False


def choose():
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_chat:
                if event.text.lower() in ["да", "конечно", "этого"]:
                    return True
                elif event.text.lower() == "нет" or \
                        (event.text.lower() in ["нет конечно", "не этого"]):
                    return False


def zapusk():
    count = -1
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_chat:
                count += 1
                if event.text.lower() == "начать":
                    main(event.chat_id)
                else:
                    if count % 10 == 0:
                        MESSAGE = "🔸Напоминание\n--что бы" \
                            "воспользоваться ботом введите:\n'Начать'"
                        vk.messages.send(chat_id=event.chat_id,
                                         message=MESSAGE,
                                         random_id=random.randint(0, 2 ** 64))


def main(a):
    morph = pymorphy2.MorphAnalyzer()
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    MESSAGE = "🔅Бот погода🔅\n\n🔸Для чего нужен этот бот?\n--Данный бог  \
        говорит погоду на ближайшее время, указанного города России\n \
        --На данный момент бот может узнать погоду лишь на сегодняшний и  \
        завтрашний день\n\n🔸Как пользоваться данным ботом\n--Нужно \
        ввести запрос, где будет слово 'погода', название города и указано  \
        на сегодня или завтра  вы хотите \
        узнать погоду\n--В случае если город не будет указан,  \
        бот будет задавать новодящие вопросы(если не указать на сегодня  \
        или завтра нужна погода, по умолчанию бот скажет погоду на сегодня)\
        \n\n🔸Чтобы закончить работу с ботом введите:\n'выход'"
    vk.messages.send(chat_id=a, message=MESSAGE, 
                     random_id=random.randint(0, 2 ** 64))
    for event in longpoll.listen():
        city = ""
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if "погод" in event.text.lower() or event.text.lower() == "погода" \
               or "прогноз" in event.text.lower():
                zapr = event.text.lower()
                for elem in zapr.split():
                    word = morph.parse(elem)[0]
                    if 'NOUN' in word.tag.POS:
                        word = word.inflect({'nomn'}).word
                    else:
                        word = elem
                    with open("ru.txt", "r") as names:
                        names = names.read().split()
                        if word.capitalize() in names:
                            city = word
                        else:
                            pass
                if city == "":
                    response1 = vk.users.get(user_id=event.user_id, 
                                             fields="city")
                    try:
                        city = response1[0]["city"]["title"]
                    except KeyError:
                        MESSAGE = "погоду какого города вы бы хотели узнать?\n"
                        vk.messages.send(chat_id=event.chat_id, 
                                         message=MESSAGE, 
                                         random_id=random.randint(0, 2 ** 64))
                        city_name = choose_city()
                        if city_name:
                            MESSAGE = f"погода {city_name}"
                            vk.messages.send(chat_id=event.chat_id, 
                                             message=MESSAGE,
                                             random_id=random.randint(0, 2 
                                                                      ** 64))
                            MESSAGE = weather(city_name, API, zapr)
                            vk.messages.send(chat_id=event.chat_id, 
                                             message=MESSAGE,
                                             random_id=random.randint(0, 2 ** 
                                                                      64))
                        else:
                            while not city_name:
                                MESSAGE = "погоду какого города вы бы \
                                хотели узнать?\n"
                                vk.messages.send(chat_id=event.chat_id, 
                                                 message=MESSAGE,
                                                 random_id=random.randint(0, 2 
                                                                          ** 
                                                                          64))
                                city_name = choose_city()
                    else:
                        MESSAGE = \
                            f"погоду этого города вы хотите узнать: {city}?"
                        vk.messages.send(chat_id=event.chat_id, 
                                         message=MESSAGE, 
                                         random_id=random.randint(0, 2 ** 64))
                        if choose():
                            city_name = response1[0]['city']['title']
                            MESSAGE = f"погода {city_name}"
                            vk.messages.send(chat_id=event.chat_id, 
                                             message=MESSAGE,
                                             random_id=random.randint(0, 2 ** 
                                                                      64))
                            zapr = event.text.lower()
                            MESSAGE = weather(city_name, API, zapr)
                            vk.messages.send(chat_id=event.chat_id, 
                                             message=MESSAGE,
                                             random_id=random.randint(0, 2 ** 
                                                                      64))
                        else:
                            MESSAGE = "погоду какого города вы бы хотели узнать"
                            vk.messages.send(chat_id=event.chat_id, 
                                             message=MESSAGE,
                                             random_id=random.randint(0, 2 ** 
                                                                      64))
                            city_namee = choose_city()
                            if city_namee:
                                MESSAGE = weather(city_namee, API, zapr)
                                vk.messages.send(chat_id=event.chat_id, 
                                                 message=MESSAGE,
                                                 random_id=random.randint(0, 2 
                                                                          ** 
                                                                          64))
                            else:
                                while not city_namee:
                                    MESSAGE = "Такого города не" \
                                        "существует\nназовите другой город"
                                    vk.messages.send(chat_id=event.chat_id, 
                                                     message=MESSAGE,
                                                     random_id=random.randint(0,
                                                                              2 
                                                                              **
                                                                              64
                                                                              ))
                                    city_namee = choose_city()
                                MESSAGE = weather(city_namee, API, zapr)
                                vk.messages.send(chat_id=event.chat_id, 
                                                 message=MESSAGE,
                                                 random_id=random.randint(0, 2 
                                                                          ** 64))

                else:
                    MESSAGE = f"погода {city}"
                    vk.messages.send(chat_id=event.chat_id, message=MESSAGE, 
                                     random_id=random.randint(0, 2 ** 64))
                    MESSAGE = weather(city, API, zapr)
                    vk.messages.send(chat_id=event.chat_id, message=MESSAGE, 
                                     random_id=random.randint(0, 2 ** 64))

            if ("что" in event.text.lower()) and ("умеешь" in event.text.lower()
                                                  or "можешь" in
                                                  event.text.lower()) or \
               event.text.lower() == "помощь":
                MESSAGE = "🔅Бот погода🔅\n\n🔸Для чего нужен этот бот \
                ?\n--Данный бог \
                говорит погоду на ближайшее время, указанного города России\n \
                --На данный момент бот может узнать погоду \
                лишь на сегодняшний и \
                завтрашний день\n\n🔸Как пользоваться данным ботом\n--Нужно \
                ввести запрос, где будет слово 'погода', \
                название города и указано на сегодня или завтра  вы хотите \
                узнать погоду\n--В случае если город не будет указан,  \
                бот будет задавать новодящие вопросы(если не \
                указать на сегодня или завтра нужна погода, по умолчанию \
                бот скажет погоду на сегодня)\n\n🔸Чтобы закончить работу \
                с ботом введите:\n'выход'"
                vk.messages.send(chat_id=event.chat_id, message=MESSAGE, 
                                 random_id=random.randint(0, 2 ** 64))
            if "выход" in event.text.lower().split():
                zapusk()


if __name__ == '__main__':
    zapusk()