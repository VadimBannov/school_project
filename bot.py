import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import time
from gpt import (
    create_system_prompt,
    ask_gpt,
    user_data,
    user_collection
)
from database import *
from config import *


# Токен и класс GPT
bot = telebot.TeleBot(BOT_TOKEN)

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


@bot.message_handler(commands=["request_history"])
@bot.message_handler(func=lambda message: "История запросов" in message.text)
def command_history(message):
    user_id = message.from_user.id

    user_all_history = get_history_and_date(user_id)

    if user_all_history:
        history_text = ""
        for history_item in user_all_history:
            history_text += f"{history_item['date']}: ({history_item['content']})\n"
        bot.send_message(message.chat.id, f"Ваши все истории подарков:\n{history_text}")
    else:
        bot.send_message(message.chat.id, "У вас нет истории запросов.")

    return


@bot.message_handler(commands=["start"])
def start_command(message):
    user_name, user_id = message.from_user.first_name, message.from_user.id

    if not is_value_in_table(DB_TABLE_USERS_NAME, "user_id", user_id):
        insert_row(
            [
                user_id,
                None,
                None,
                None
            ]
        )

    if user_id not in user_data:
        user_data[user_id] = {
            'holiday': None,
            'recipient': None,
            'age': None,
        }
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
                                       "Пересоздать: После получения ответа, если вас не устроил ответ, вы сможете его "
                                       "пересоздать.\n\n"
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
    user_id = message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return

    bot.send_message(message.chat.id, "Выберите кому вы хотите подарить подарок: ",
                     reply_markup=create_markup(["Ребенку", "Родителям", "Родственнику", "Другу/подруге"]))
    bot.register_next_step_handler(message, processing_selected_recipient)
    return


@bot.message_handler(commands=['recreate_explaining'])
@bot.message_handler(func=lambda message: "Пересоздать" in message.text)
def continue_commands(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    bot.send_message(message.chat.id, "Подождите чутка", reply_markup=ReplyKeyboardRemove())
    time.sleep(2)
    generating_gift(message)
    return


@bot.message_handler(commands=['end_dialog'])
@bot.message_handler(func=lambda message: "Завершить" in message.text)
def end_task_commands(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    user_data[user_id] = {
        'genre': None,
        'character': None,
        'setting': None,
        'additional_info': ''
    }
    time.sleep(2)
    bot.send_message(message.chat.id, "Текущий диалог завершено",
                     reply_markup=ReplyKeyboardRemove())
    start_command(message)
    return


@bot.message_handler()
def processing_selected_holiday(message):
    message_text, user_id = message.text, message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return

    if message_text == "День рождения":
        user_data[user_id]["holiday"] = "День рождения"
    elif message_text == "Новый год":
        user_data[user_id]["holiday"] = "Новый год"
    elif message_text == "14 февраля":
        user_data[user_id]["holiday"] = "14 февраля"
    elif message_text == "23 февраля":
        user_data[user_id]["holiday"] = "23 февраля"
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

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return

    if message_text == "Ребенку":
        user_data[user_id]["recipient"] = "Ребенку"
        subclass_parameters = ["Мальчику", "Девочке", "Назад"]
    elif message_text == "Родителям":
        user_data[user_id]["recipient"] = "Родителям"
        subclass_parameters = ["Маме", "Папе", "Назад"]
    elif message_text == "Родственнику":
        user_data[user_id]["recipient"] = "Родственнику"
        subclass_parameters = ["Бабушке", "Дедушке", "Тёте", "Дяде", "Назад"]
    elif message_text == "Другу/подруге":
        user_data[user_id]["recipient"] = "Другу/подруге"
        subclass_parameters = ["Другу", "Подруге", "Назад"]
    elif message_text == "Назад":
        command_help_with_holiday(message)
        return
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return

    bot.send_message(message.chat.id, "А кому именно?", reply_markup=create_markup(subclass_parameters))
    bot.register_next_step_handler(message, internal_verification)


def internal_verification(message):
    message_text, user_id = message.text, message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    if message_text == "Мальчику":
        user_data[user_id]["recipient"] = "Мальчику"
    elif message_text == "Девочке":
        user_data[user_id]["recipient"] = "Девочке"
    elif message_text == "Маме":
        user_data[user_id]["recipient"] = "Маме"
        confirming_message(message)
        return
    elif message_text == "Папе":
        user_data[user_id]["recipient"] = "Папе"
        confirming_message(message)
        return
    elif message_text == "Бабушке":
        user_data[user_id]["recipient"] = "Бабушке"
        confirming_message(message)
        return
    elif message_text == "Дедушке":
        user_data[user_id]["recipient"] = "Дедушке"
        confirming_message(message)
        return
    elif message_text == "Тёте":
        user_data[user_id]["recipient"] = "Тёте"
        confirming_message(message)
        return
    elif message_text == "Дяде":
        user_data[user_id]["recipient"] = "Дяде"
        confirming_message(message)
        return
    elif message_text == "Другу":
        user_data[user_id]["recipient"] = "Другу"
    elif message_text == "Подруге":
        user_data[user_id]["recipient"] = "Подруге"
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
                   reply_markup=create_markup(["Младше 12", "От 12 до 18", "От 18 до 24", "Старше 24", "Назад"]))
    bot.register_next_step_handler(message, indication_age)


def indication_age(message):
    message_text, user_id = message.text, message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    if message_text == "Младше 12":
        user_data[user_id]["age"] = "Младше 12"
    elif message_text == "От 12 до 18":
        user_data[user_id]["age"] = "От 12 до 18"
    elif message_text == "От 18 до 24":
        user_data[user_id]["age"] = "От 18 до 24"
    elif message_text == "Старше 24":
        user_data[user_id]["age"] = "Старше 24"
    elif message_text == "Назад":
        if get_data_for_user(user_id)["recipient"] in ["Мальчику", "Девочке"]:
            bot.send_message(message.chat.id, "А кому именно?",
                             reply_markup=create_markup(["Мальчику", "Девочке", "Назад"]))
        elif get_data_for_user(user_id)["recipient"] in ["Другу", "Подруге"]:
            bot.send_message(message.chat.id, "А кому именно?",
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

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    holiday, recipient, age = (user_data[user_id]['holiday'], user_data[user_id]['recipient'],
                               user_data[user_id]['age'])
    if user_data[user_id]["age"] is None:
        age = "Определен автоматический"
    bot.send_message(message.chat.id, f"Вы действительно хотите применить эти параметры?\n\n"
                     f"Праздник: ({holiday});\nКому: ({recipient});\nВозраст: ({age})",
                     reply_markup=create_markup(["Применить", "Изменить"]))
    bot.register_next_step_handler(message, generating_gift)


def generating_gift(message):
    message_text, user_id = message.text, message.from_user.id

    if user_id not in user_data:
        start_command(message)
        return
    elif user_data[user_id]["holiday"] is None:
        command_help_with_holiday(message)
        return
    elif user_data[user_id]["recipient"] is None:
        command_help_with_recipient(message)
        return

    if message.content_type != "text":
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        bot.register_next_step_handler(message, generating_gift)
        return

    if message_text == "Изменить":
        user_data[user_id] = {
            'genre': None,
            'character': None,
            'setting': None,
            'additional_info': ''
        }
        time.sleep(1)
        start_command(message)
        return
    if message_text == "Пересоздать" or message_text == "Применить":
        user_collection[user_id] = [
            {'role': 'system', 'content': create_system_prompt(user_data, user_id)},
        ]
        insert_row(
            [
                user_id,
                'system',
                create_system_prompt(user_data, user_id),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            ]
        )
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите клавиатурную кнопку!")
        return

    bot.send_message(message.chat.id, "Ответ генерируется. Пожалуйста, подождите некоторое время",
                     reply_markup=ReplyKeyboardRemove())

    assistant_content = ask_gpt(user_collection[user_id])
    user_collection[user_id].append({'role': 'assistant', 'content': assistant_content})
    insert_row(
        [
            user_id,
            'assistant',
            assistant_content,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        ]
    )
    bot.send_message(message.chat.id, f'Ваш подарок: {assistant_content}',
                     reply_markup=create_markup(["Пересоздать", "Завершить", "История запросов"]))
    time.sleep(2)
    bot.send_message(message.chat.id, 'Для пересоздания ответа нажмите «Пересоздать». Чтобы закончить нажмите '
                                      '«Завершить»')


bot.polling()
