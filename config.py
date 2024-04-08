BOT_TOKEN = "6506811778:AAE0kCSpPuyVSq8iHI5f_5J4mB7sTGPUU58"  # подставь свой токен

GPT_LOCAL_URL = "http://localhost:1234/v1/chat/completions"  # подставь свой локальный url-адрес
HEADERS = {"Content-Type": "application/json"}
MAX_TOKENS = 150

DB_DIR = 'db'
DB_NAME = 'gpt_helper.db'
DB_TABLE_USERS_NAME = 'users'


SYSTEM_PROMPT = ("Ты даешь рекомендации по выбору подарков для пользователей, и тебе следует учитывать современные "
                 "тенденции, чтобы предоставлять актуальные рекомендации. Вместо того чтобы предлагать несколько "
                 "вариантов, ты должен сосредоточиться на одном подарке.")

LINK_IMAGE = {
    0: "https://ibb.co/ngLYSnF",
    1: "https://ibb.co/7XCMsBS",
    2: "https://ibb.co/CW751CJ"
}
