import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import time
from config import *
from gpt import GPT
from database import *

# Токен и класс GPT
bot = telebot.TeleBot(BOT_TOKEN)
gpt = GPT()

# Создания таблицы и проверка
prepare_db()
get_all_rows(DB_TABLE_USERS_NAME)

# Выведение ошибок с помощью Logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt", filemode="a",
)


# Функция для создание кнопок
def create_markup(button_labels):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for label in button_labels:
        markup.add(KeyboardButton(label))
    return markup


# debug и история запросов
@bot.message_handler(commands=['debug'])
def debug_command(message):
    with open("log_file.txt", "r", encoding="latin1") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=["history"])
@bot.message_handler(func=lambda message: "История запросов" in message.text)
def command_history(message):
    user_id = message.from_user.id
    history = get_data_for_user(user_id)
    if history:
        history_text = f"{history['timestamp']}:  ({history['task']})  -  ({history['answer']})"
        bot.send_message(message.chat.id, f"Ваша история запросов:\n{history_text}")
    else:
        bot.send_message(message.chat.id, "У вас нет истории запросов.")


@bot.message_handler(commands=["start"])
def start_command(message):
    user_name, user_id = message.from_user.first_name, message.from_user.id
    if is_value_in_table(DB_TABLE_USERS_NAME, "user_id", user_id):
        delete_user(user_id)
    insert_row([user_id, 'null', 'null', 'null', 'null', 'null', "null"])
    bot.send_photo(message.chat.id, LINK_IMAGE[0], f"Здравствуй {user_name}! Вас приветствует бот «Мир "
                                                   f"подарков». Чтобы бот написал ваш подарок, "
                                                   f"вам необходимо указать некоторые параметры. Или можно посмотреть "
                                                   f"инструкцию по пользованию бота, или его описание.\n\n"
                                                   "Выберите праздник:",
                   reply_markup=create_markup(["День рождения", "Новый год", "14 февраля", "23 февраля", "⟶"]))


@bot.message_handler(func=lambda message: "⟶" in message.text)
def other_options(message):
    bot.send_message(message.chat.id, "⟶",
                     reply_markup=create_markup(["📚Инструкция", "🤖Описание бота", "⟵"]))


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda message: "📚Инструкция" in message.text)
def help_command(message):
    message_text = message.text
    bot.send_message(message.chat.id,  "——————————————————————\n"
                                       "📚Инструкция по использованию бота «Мир подарков»\n\n\n"
                                       "Приветствуем вас в боте «Мир подарков»! Этот бот поможет вам выбрать идеальный "
                                       "подарок для ваших близких на различные праздники. Вот как им "
                                       "пользоваться:\n\n\n"
                                       "Выбор праздника: Выберите праздник из предложенных вариантов.\n\n"
                                       "Выбор получателя подарка: Укажите, кому вы хотите сделать подарок, "
                                       "выбрав из предложенных вариантов.\n\n"
                                       "Уточнение возраста: Если необходимо, Укажите возраст получателя подарка, "
                                       "выбрав один из предложенных диапазонов возраста.\n\n"
                                       "Получение рекомендации: Бот сгенерирует рекомендацию подарка на основе "
                                       "выбранных вами параметров.\n\n"
                                       "Продолжить: После получения ответа, если вы заметили, что бот не дописал "
                                       "полностью ответ, вы можете нажать кнопку «Продолжить», и тогда бот допишет "
                                       "его, и вы сможете увидеть ответ полностью.\n\n"
                                       "Завершение диалога: По завершении диалога вы можете начать новый диалог или "
                                       "запросить историю предыдущих запросов с помощью соответствующих кпонок.\n"
                                       "——————————————————————",
                     reply_markup=create_markup(["📚Инструкция", "🤖Описание бота", "⟵"]))
    if message_text == "/help":
        bot.send_message(message.chat.id, "Клавиатурные кнопки были убраны", reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=["about"])
@bot.message_handler(func=lambda message: "🤖Описание бота" in message.text)
def about_command(message):
    message_text = message.text
    bot.send_message(message.chat.id, "——————————————————————\n"
                                      "🤖Описание бота «Мир подарков»\n\n\n"
                                      "Бот «Мир подарков» - это умный помощник, который поможет вам выбрать идеальный "
                                      "подарок для ваших близких на различные праздники. Этот бот предложит вам "
                                      "рекомендации, которые точно понравятся вашим друзьям и семье.\n\n\n"
                                      "Основные функции:\n\n\n"
                                      "Персонализированные рекомендации: Бот анализирует ваши параметры подарка "
                                      "(праздник, получатель, возраст) и предлагает подходящие подарки.\n\n"
                                      "Широкий выбор праздников: Выбирайте подарки для различных праздников, чтобы "
                                      "сделать их особенными и запоминающимися.\n\n"
                                      "Простой в использовании: Интуитивно понятный интерфейс бота позволяет легко и "
                                      "быстро выбрать подходящий подарок.\n\n"
                                      "История запросов: Следите за предыдущими запросами и полученными рекомендациями"
                                      " с помощью функции истории запросов.\n\n"
                                      "Поддержка разных возрастных категорий: Бот учитывает возраст получателя подарка"
                                      " и предлагает рекомендации, соответствующие его интересам и предпочтениям.\n\n\n"
                                      "Не теряйте время на поиск идеального подарка в магазинах - доверьтесь боту "
                                      "«Мир подарков» и сделайте праздник незабываемым для ваших близких!\n"
                                      "——————————————————————",
                     reply_markup=create_markup(["📚Инструкция", "🤖Описание бота", "⟵"]))
    if message_text == "/about":
        bot.send_message(message.chat.id, "Клавиатурные кнопки были убраны", reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=["help_with_holiday"])
def command_help_with_holiday(message):
    bot.send_message(message.chat.id, "Выберите праздник: ",
                     reply_markup=create_markup(["День рождения", "Новый год", "14 февраля", "23 февраля"]))
    bot.register_next_step_handler(message, processing_selected_holiday)
    return


@bot.message_handler(commands=["help_with_recipient"])
def command_help_with_recipient(message):
    bot.send_message(message.chat.id, "Выберите кому вы хотите подарить подарок: ",
                     reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге"]))
    bot.register_next_step_handler(message, processing_selected_recipient)
    return


@bot.message_handler(commands=['continue_explaining'])
@bot.message_handler(func=lambda message: "Продолжить" in message.text)
def continue_commands(message):
    if (is_value_in_table(DB_TABLE_USERS_NAME, "holiday", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "recipient", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "age", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "task", "null")):
        if is_value_in_table(DB_TABLE_USERS_NAME, "holiday", "null"):
            bot.send_message(message.chat.id, "Сначала выберите праздник: ",
                             reply_markup=create_markup(["День рождения", "Новый год", "14 февраля", "23 февраля"]))
            bot.register_next_step_handler(message, processing_selected_holiday)
            return
        elif is_value_in_table(DB_TABLE_USERS_NAME, "recipient", "null"):
            bot.send_message(message.chat.id, "Сначала выберите кому вы хотите подарить подарок: ",
                             reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге"]))
            bot.register_next_step_handler(message, processing_selected_recipient)
            return
        elif is_value_in_table(DB_TABLE_USERS_NAME, " age", "null"):
            bot.send_message(message.chat.id,
                             "Сначала укажите возраст человека, которому вы хотите подарить подарок:",
                             reply_markup=create_markup(["Младше 12", "12-18", "18-24", "Старше 24"]))
            bot.register_next_step_handler(message, indication_age)
            return
        else:
            bot.send_message(message.chat.id, "Сначала необходимо указать некоторые параметры ")
            bot.register_next_step_handler(message, start_command)
            return
    bot.send_message(message.chat.id, "Подождите чутка", reply_markup=ReplyKeyboardRemove())
    generating_gift(message)
    return


@bot.message_handler(commands=['end_dialog'])
@bot.message_handler(func=lambda message: "Завершить" in message.text)
def end_task_commands(message):
    if (is_value_in_table(DB_TABLE_USERS_NAME, "holiday", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "recipient", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "age", "null") or
            is_value_in_table(DB_TABLE_USERS_NAME, "task", "null")):
        if is_value_in_table(DB_TABLE_USERS_NAME, "holiday", "null"):
            bot.send_message(message.chat.id, "Сначала выберите праздник: ",
                             reply_markup=create_markup(["День рождения", "Новый год", "14 февраля", "23 февраля"]))
            bot.register_next_step_handler(message, processing_selected_holiday)
            return
        elif is_value_in_table(DB_TABLE_USERS_NAME, "recipient", "null"):
            bot.send_message(message.chat.id, "Сначала выберите кому вы хотите подарить подарок: ",
                             reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге"]))
            bot.register_next_step_handler(message, processing_selected_recipient)
            return
        elif is_value_in_table(DB_TABLE_USERS_NAME, " age", "null"):
            bot.send_message(message.chat.id,
                             "Сначала укажите возраст человека, которому вы хотите подарить подарок:",
                             reply_markup=create_markup(["Младше 12", "12-18", "18-24", "Старше 24"]))
            bot.register_next_step_handler(message, indication_age)
            return
        else:
            bot.send_message(message.chat.id, "Сначала необходимо указать некоторые параметры ")
            bot.register_next_step_handler(message, start_command)
            return
    time.sleep(2)
    bot.send_message(message.chat.id, "Текущий диалог завершено",
                     reply_markup=ReplyKeyboardRemove())
    start_command(message)
    return


@bot.message_handler()
def processing_selected_holiday(message):
    message_text, user_id = message.text, message.from_user.id
    if message_text == "День рождения":
        update_row_value(user_id, "holiday", "birthday")
    elif message_text == "Новый год":
        update_row_value(user_id, "holiday", "new year")
    elif message_text == "14 февраля":
        update_row_value(user_id, "holiday", "14th february")
    elif message_text == "23 февраля":
        update_row_value(user_id, "holiday", "23th february")
    elif message_text == "⟵":
        start_command(message)
        return
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return
    bot.send_photo(message.chat.id,  LINK_IMAGE[1], "А теперь выберите кому вы хотите подарить подарок: ",
                   reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге", "Назад"]))
    bot.register_next_step_handler(message, processing_selected_recipient)


def processing_selected_recipient(message):
    message_text, user_id = message.text, message.from_user.id
    if is_value_in_table(DB_TABLE_USERS_NAME, "holiday", "null"):
        bot.send_message(message.chat.id, "Сначала выберите праздник: ",
                         reply_markup=create_markup(["День рождения", "Новый год", "14 февраля", "23 февраля"]))
        bot.register_next_step_handler(message, processing_selected_holiday)
        return
    if message_text == "Ребенку":
        update_row_value(user_id, "recipient", "child")
        subclass_parameters = ["Мальчику", "Девочке", "Назад"]
    elif message_text == "Родителям":
        update_row_value(user_id, "recipient", "parents")
        subclass_parameters = ["Маме", "Папе", "Назад"]
    elif message_text == "Родственнику":
        update_row_value(user_id, "recipient", "relative")
        subclass_parameters = ["Бабушке", "Дедушке", "Тёти", "Дяди", "Назад"]
    elif message_text == "Другу/подруге":
        update_row_value(user_id, "recipient", "friend or girlfriend")
        subclass_parameters = ["Другу", "Подруге", "Назад"]
    elif message_text == "Назад":
        command_help_with_holiday(message)
        return
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return
    bot.send_message(message.chat.id, "А именно?", reply_markup=create_markup(subclass_parameters))
    bot.register_next_step_handler(message, internal_verification)


def internal_verification(message):
    message_text, user_id = message.text, message.from_user.id
    if message_text == "Мальчику":
        update_row_value(user_id, "recipient", "boy")
    elif message_text == "Девочке":
        update_row_value(user_id, "recipient", "girl")
    elif message_text == "Маме":
        update_row_value(user_id, "recipient", "mom")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Папе":
        update_row_value(user_id, "recipient", "dad")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Бабушке":
        update_row_value(user_id, "recipient", "grandmother")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Дедушке":
        update_row_value(user_id, "recipient", "grandfather")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Тёти":
        update_row_value(user_id, "recipient", "aunt")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Дяди":
        update_row_value(user_id, "recipient", "uncle")
        update_row_value(user_id, "age", "not necessary")
        confirming_message(message)
        return
    elif message_text == "Другу":
        update_row_value(user_id, "recipient", "friend")
    elif message_text == "Подруге":
        update_row_value(user_id, "recipient", "girlfriend")
    elif message_text == "Назад":
        bot.send_message(message.chat.id, "Выберите кому вы хотите подарить подарок: ",
                         reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге", "Назад"]))
        bot.register_next_step_handler(message, processing_selected_recipient)
        return
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return
    bot.send_photo(message.chat.id, LINK_IMAGE[2],
                   "Укажите возраст человека, которому вы хотите подарить подарок: ",
                   reply_markup=create_markup(["Младше 12", "12-18", "18-24", "Старше 24", "Назад"]))
    bot.register_next_step_handler(message, indication_age)


def indication_age(message):
    message_text, user_id = message.text, message.from_user.id
    if message_text == "Младше 12":
        update_row_value(user_id, "age", "under 12")
    elif message_text == "12-18":
        update_row_value(user_id, "age", "from 12 to 18")
    elif message_text == "18-24":
        update_row_value(user_id, "age", "from 18 to 24")
    elif message_text == "Старше 24":
        update_row_value(user_id, "age", "older 24")
    elif message_text == "Назад":
        if get_data_for_user(user_id)["recipient"] == "boy" or get_data_for_user(user_id)["recipient"] == "girl":
            bot.send_message(message.chat.id, "А именно?",
                             reply_markup=create_markup(["Мальчику", "Девочке", "Назад"]))
        elif (get_data_for_user(user_id)["recipient"] == "friend" or
              get_data_for_user(user_id)["recipient"] == "girlfriend"):
            bot.send_message(message.chat.id, "А именно?",
                             reply_markup=create_markup(["Другу", "Подруге", "Назад"]))
        else:
            bot.send_message(message.chat.id, "Выберите кому вы хотите подарить подарок: ",
                             reply_markup=create_markup(
                                 ["Ребенку", "Родителям", "Родственнику", "Другу/подруге", "Назад"]))
            bot.register_next_step_handler(message, processing_selected_recipient)
            return
        bot.register_next_step_handler(message, internal_verification)
        return
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
    confirming_message(message)


def confirming_message(message):
    message_text, user_id = message.text, message.from_user.id
    res, second_res, third_res = (get_data_for_user(user_id)['holiday'],
                                  get_data_for_user(user_id)['recipient'], get_data_for_user(user_id)['age'])
    if res == "birthday":
        holiday = "День рождения"
    elif res == "new year":
        holiday = "Новый год"
    elif res == "14th february":
        holiday = "14 февраля"
    else:
        holiday = "23 февраля"
    if second_res == "boy":
        recipient = "Мальчику"
    elif second_res == "girl":
        recipient = "Девочке"
    elif second_res == "mom":
        recipient = "Маме"
    elif second_res == "dad":
        recipient = "Папе"
    elif second_res == "grandmother":
        recipient = "Бабушке"
    elif second_res == "grandfather":
        recipient = "Дедушке"
    elif second_res == "aunt":
        recipient = "Тёти"
    elif second_res == "uncle":
        recipient = "Дяди"
    elif second_res == "friend":
        recipient = "Другу"
    else:
        recipient = "Подруге"
    if third_res == "under 12":
        age = "Младше 12"
    elif third_res == "from 12 to 18":
        age = "12-18"
    elif third_res == "from 18 to 24":
        age = "18-24"
    elif third_res == "older 24":
        age = "Старше 24"
    else:
        age = "Определен автоматический"
    bot.send_message(message.chat.id, f"Вы действительно хотите применить эти параметры?\n\n"
                     f"Праздник: ({holiday});\nКому: ({recipient});\nВозраст: ({age})",
                     reply_markup=create_markup(["Применить", "Изменить"]))
    bot.register_next_step_handler(message, generating_gift)


def generating_gift(message):
    message_text, user_id = message.text, message.from_user.id
    if message.content_type != "text":
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        bot.register_next_step_handler(message, generating_gift)
        return
    if message_text == "Изменить":
        start_command(message)
        return
    if message_text == "Продолжить" or message_text == "Применить":
        pass
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return
    bot.send_message(message.chat.id, "Ответ генерируется. Пожалуйста, подождите некоторое время",
                     reply_markup=ReplyKeyboardRemove())
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    update_row_value(user_id, "timestamp", formatted_time)
    res, second_res, third_res = (get_data_for_user(user_id)['holiday'],
                                  get_data_for_user(user_id)['recipient'],
                                  get_data_for_user(user_id)["age"])
    update_row_value(user_id, "task", PROMPTS_TEMPLATES[res][second_res][third_res])
    system_prompt = ("Ты - бот-помощик по рекомендации подарки, и твоя задача — давать короткие и стильные "
                     "рекомендации по выбору подарка, учитывая современные тренды.")

    dictionary_from_database = get_data_for_user(user_id)
    promt = gpt.make_promt(dictionary_from_database, system_prompt)
    resp = gpt.send_request(promt)
    success, answer = gpt.process_resp(resp)
    update_row_value(user_id, "answer", answer)

    bot.send_message(message.chat.id, get_data_for_user(user_id)['answer'],
                     reply_markup=create_markup(["Продолжить", "Завершить", "История запросов"]))


bot.polling()
