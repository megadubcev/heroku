import vk_api
import random
import sqlite3
import json
import logging
import datetime
import requests

logging.basicConfig(filename='example.log')

from math2 import primer, uravnenie, uravnenie2

from geo import continent, capital, flagi, sqare

vk = vk_api.VkApi(token="424d63642ffd83aabe9fc26a0efd897e056f7dcef61c9f82bde477fcbcd358bc2fadd339f3dd169dcc51e")


class DB:
    def __init__(self):
        conn = sqlite3.connect('bot.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (user_id INTEGER,
                             user_name VARCHAR(50),
                             user_surename VARCHAR(50),
                             context VARCHAR(50),
                             reiting INTEGER,
                             place INTEGER,
                             answerInt INTEGER,
                             answerText VARCHAR(50)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_id, user_name, user_surename, context, reiting, place, answerInt, answerText):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                          (user_id, user_name, user_surename, context, reiting, place, answerInt, answerText)
                          VALUES (?,?,?,?,?,?,?,?)''',
                       (user_id, user_name, user_surename, context, reiting, place, answerInt, answerText))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return True if row else False

    def reiting(self, user_id, increase=1):
        cursor = self.connection.cursor()
        newReiting = increase + userDB.get(user_id)[4]
        cursor.execute("UPDATE users SET reiting = ? where user_id = ?", (str(newReiting), str(user_id)))
        self.connection.commit()

    def context(self, user_id, context):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET context = ? where user_id = ?", (str(context), str(user_id)))
        self.connection.commit()

    def answerInt(self, user_id, answer):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET answerInt = ? where user_id = ?", (str(answer), str(user_id)))
        self.connection.commit()

    def answerText(self, user_id, answer):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET answerText = ? where user_id = ?", (str(answer), str(user_id)))
        self.connection.commit()

    def place(self, user_id, place):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET place = ? where user_id = ?", (str(place), str(user_id)))
        self.connection.commit()


def get_tokens(body):
    znaki = "!.,?:()[]'"
    tokens = body.lower().split()
    for i in range(len(tokens)):
        for znak in znaki:
            tokens[i] = "".join(tokens[i].split(znak))
    return tokens


def isChislo(text):
    try:
        a = int(text)
        return True
    except:
        return False


def get_number(tokens):
    for token in tokens:
        if isChislo(token):
            return token
    return None


def get_numbers(tokens):
    n = 0
    spisok = [None, None]
    for token in tokens:
        if isChislo(token):
            spisok[n] = int(token)
            n += 1
        if n == 2:
            break
    if n == 2:
        if spisok[0] > spisok[1]:
            t = spisok[0]
            spisok[0] = spisok[1]
            spisok[1] = t
        return str(spisok[0]) + ' ' + str(spisok[1])
    return None


def sort_top():
    users = sorted(userDB.get_all(), key=lambda x: x[4], reverse=True)
    for i in range(len(users)):
        userDB.place(users[i][0], i + 1)
    return users[:5]


def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


def photo(name):
    fname = "flagi2/" + name + ".png"
    f = open(fname, "rb")
    print(f)
    a = vk.method('photos.getMessagesUploadServer')
    b = requests.post(a['upload_url'], files={'photo': f}).json()
    print(b['photo'])
    print(b['server'])
    print(b['hash'])
    c = vk.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
    d = 'photo{}_{}'.format(c['owner_id'], c['id'])
    return d


def get_keyboard(labels):
    buttons = []
    for i in range(len(labels)):
        buttons.append([])
        for j in range(len(labels[i])):
            buttons[i].append(get_button(label=labels[i][j], color="primary"))
    keyboard = {
        "one_time": True,
        "buttons": buttons
    }
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def log_to_file(date, e):
    logging.warning(date + ' ' + e)


db = DB()
userDB = UsersModel(db.get_connection())
userDB.init_table()

while True:
    try:
        messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unread"})
        if messages["count"] >= 1:
            id = messages["items"][0]["last_message"]["from_id"]
            body = messages["items"][0]["last_message"]["text"]
            print(body.lower(), id, messages["items"][0]["last_message"])
            user = vk.method("users.get", {"user_ids": id})[0]
            print(user)
            user_name = user["first_name"]
            user_surename = user["last_name"]
            print(userDB.get_all())
            tokens = get_tokens(body)
            print(tokens)

            vk.method("messages.markAsRead",
                      {"peer_id": id})

            if not userDB.exists(id):
                userDB.insert(id, user_name, user_surename, "меню", 0, 0, None, None)
                vk.method("messages.send",
                          {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                           "message": "Привет, " + user_name + "!\n Выбери нужную функцию",
                           "keyboard": get_keyboard([['рейтинг', 'играть']])})

            elif userDB.get(id)[3] == "меню":
                if "рейтинг" in tokens:
                    usersTop = sort_top()
                    text = 'Топ 5 участников \n'
                    for i in range(len(usersTop)):
                        text += str(i + 1) + '. @id' + str(usersTop[i][0]) + '(' + str(usersTop[i][1]) + ' ' + str(
                            usersTop[i][2]) + ') ' + str(usersTop[i][4]) + '\n'
                    text += "Твои очки: " + str(userDB.get(id)[4]) + '\n Твоё место в рейтинге: ' + str(
                        userDB.get(id)[5])

                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": text, "keyboard": get_keyboard([['рейтинг', 'играть']])})


                elif "играть" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "выбери предмет",
                               "keyboard": get_keyboard([['математика', 'география'], ['меню']])})
                    userDB.context(id, "выбор предмета")


                else:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я тебя не понял", "keyboard": get_keyboard([['рейтинг', 'играть']])})


            elif userDB.get(id)[3] == "выбор предмета":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif "математика" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери сложность", "keyboard": get_keyboard([['1', '2', '3', 'меню']])})
                    userDB.context(id, "выбор сложности математика")

                elif "география" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери сложность",
                               "keyboard": get_keyboard([['1', '2', '3', '4'], ['меню']])})
                    userDB.context(id, "выбор сложности география")

                else:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я тебя не понял",
                               "keyboard": get_keyboard([['математика', 'география'], ['меню']])})


            elif userDB.get(id)[3] == "выбор сложности математика":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif "1" in tokens:
                    question = primer()
                    userDB.answerInt(id, question[1])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Сколько будет " + question[0] + "?", "keyboard": get_keyboard([['меню']])})
                    userDB.context(id, "математика1")

                elif "2" in tokens:
                    question = uravnenie()
                    userDB.answerInt(id, question[1])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Найдите корень уравнения: " + question[0],
                               "keyboard": get_keyboard([['меню']])})
                    userDB.context(id, "математика2")

                elif "3" in tokens:
                    question = uravnenie2()
                    userDB.answerText(id, question[1])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Найдите 2 корня уравнения: " + question[0],
                               "keyboard": get_keyboard([['меню']])})
                    userDB.context(id, "математика3")

                else:

                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я тебя не понял", "keyboard": get_keyboard([['1', '2', '3', 'меню']])})


            elif userDB.get(id)[3] == "математика1":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif get_number(tokens) == None:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я не вижу числа", "keyboard": get_keyboard([['меню']])})

                elif int(get_number(tokens)) == userDB.get(id)[6]:
                    question = primer()
                    userDB.answerInt(id, question[1])
                    userDB.reiting(id, 1)
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \n Сколько будет " + question[0] + "?",
                               "keyboard": get_keyboard([['меню']])})

                else:
                    text = "Неверно( \n Правильный ответ: " + str(userDB.get(id)[6])
                    question = primer()
                    userDB.answerInt(id, question[1])
                    text += "\nСколько будет " + question[0] + "?"
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000), "message": text,
                               "keyboard": get_keyboard([['меню']])})

            elif userDB.get(id)[3] == "математика2":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif get_number(tokens) == None:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я не вижу числа", "keyboard": get_keyboard([['меню']])})

                elif int(get_number(tokens)) == userDB.get(id)[6]:
                    question = uravnenie()
                    userDB.answerInt(id, question[1])
                    userDB.reiting(id, 2)
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nНайдите корень уравнения: " + question[0],
                               "keyboard": get_keyboard(['меню'])})

                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[6])
                    question = uravnenie()
                    userDB.answerInt(id, question[1])
                    text += "\nНайдите корень уравнения: " + question[0]
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000), "message": text,
                               "keyboard": get_keyboard(['меню'])})

            elif userDB.get(id)[3] == "математика3":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif get_numbers(tokens) == None:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я не вижу двух чисел", "keyboard": get_keyboard([['меню']])})

                elif get_numbers(tokens) == userDB.get(id)[7]:
                    question = uravnenie2()
                    userDB.answerText(id, question[1])
                    userDB.reiting(id, 5)
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nНайдите 2 корня уравнения: " + question[0],
                               "keyboard": get_keyboard([['меню']])})

                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[7])
                    question = uravnenie2()
                    userDB.answerText(id, question[1])
                    text += "\nНайдите 2 корня уравнения: " + question[0]
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000), "message": text,
                               "keyboard": get_keyboard([['меню']])})

            elif userDB.get(id)[3] == "выбор сложности география":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif "1" in tokens:
                    question = continent()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Какому континенту или какой части света пренадлежит " + question[0] + "?",
                               "keyboard": get_keyboard(question[1])})
                    userDB.context(id, "география1")

                elif "2" in tokens:
                    question = capital()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Определите столицу страны: " + question[0],
                               "keyboard": get_keyboard(question[1])})
                    userDB.context(id, "география2")

                elif "3" in tokens:
                    question = flagi()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Какой стране пренадлежит данный флаг",
                               "keyboard": get_keyboard(question[1]),
                               "attachment": photo(question[0])})
                    userDB.context(id, "география3")

                elif "4" in tokens:
                    question = sqare()
                    userDB.answerText(id, question[0])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выберите страну с наибольшой площадью территории",
                               "keyboard": get_keyboard(question[1])})
                    userDB.context(id, "география4")

                else:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "я тебя не понял",
                               "keyboard": get_keyboard([['1', '2', '3', '4'], ['меню']])})

            elif userDB.get(id)[3] == "география1":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif body == userDB.get(id)[7]:
                    question = continent()
                    userDB.answerText(id, question[2])
                    print(get_keyboard(question[1]))
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nКакому континенту или какой части света пренадлежит " +
                                          question[0] + "?",
                               "keyboard": get_keyboard(question[1])})
                    userDB.reiting(id, 1)
                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[7])
                    question = continent()
                    userDB.answerText(id, question[2])
                    print(get_keyboard(question[1]))
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": text + "\nКакому континенту или какой части света пренадлежит " +
                                          question[0] + "?",
                               "keyboard": get_keyboard(question[1])})

            elif userDB.get(id)[3] == "география2":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif body == userDB.get(id)[7]:
                    question = capital()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nОпределите столицу страны: " + question[0],
                               "keyboard": get_keyboard(question[1])})
                    userDB.reiting(id, 2)
                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[7])
                    question = capital()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": text + "\nОпределите столицу страны: " + question[0],
                               "keyboard": get_keyboard(question[1])})

            elif userDB.get(id)[3] == "география3":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif body == userDB.get(id)[7]:
                    question = flagi()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nКакой стране пренадлежит данный флаг?",
                               "keyboard": get_keyboard(question[1]),
                               "attachment": photo(question[0])})
                    userDB.reiting(id, 3)
                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[7])
                    question = flagi()
                    userDB.answerText(id, question[2])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": text + "\nКакой стране пренадлежит данный флаг?",
                               "keyboard": get_keyboard(question[1]),
                               "attachment": photo(question[0])})

            elif userDB.get(id)[3] == "география4":
                if "меню" in tokens:
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Выбери нужную функцию", "keyboard": get_keyboard([['рейтинг', 'играть']])})
                    userDB.context(id, "меню")

                elif body == userDB.get(id)[7]:
                    question = sqare()
                    userDB.answerText(id, question[0])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": "Абсолютно верно! \nВыберите страну с наибольшой площадью территории",
                               "keyboard": get_keyboard(question[1])})
                    userDB.reiting(id, 4)

                else:
                    text = "Неверно( \nПравильный ответ: " + str(userDB.get(id)[7])
                    question = sqare()
                    userDB.answerText(id, question[0])
                    vk.method("messages.send",
                              {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                               "message": text + "\nВыберите страну с наибольшой площадью территории",
                               "keyboard": get_keyboard(question[1])})


            else:
                vk.method("messages.send",
                          {"peer_id": id, "random_id": random.randint(-100000000, 100000000),
                           "message": "Что-то пошло не так"})

    except Exception as e:
        log_to_file(str(datetime.datetime.now()), str(e))
        print(e)
