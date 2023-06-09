from os import getenv
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO
from rich.logging import RichHandler
from pyllamacpp.model import Model
from telebot import TeleBot, types
load_dotenv()

# .env
token = getenv("TELEGRAM_BOT_ID")
model_path = getenv("MODEL_PATH_2")

# Logs
basicConfig(format="%(message)s",
            datefmt="[%Y-%m-%d %X]",
            level=INFO,
            handlers=[RichHandler()])
logger = getLogger("rich")

# Configs
model_config=dict()
prompt_config = dict(
    n_threads=8,
    n_batch=3,
    temp=0.1,
    top_k=40,
    top_p=0.95,
    repeat_last_n=64,
    repeat_penalty=1.3,
    n_predict=64
)

def Bot():
    gpt = Model(ggml_model=model_path, **model_config)
    logger.info("GPT4All started")
    bot = TeleBot(token)
    logger.info("Bot started")
        
    def chatting(chat, sender, msg, reply_to):
        logger.info(f"[{chat if chat else 'Private'} | {sender}]: {msg}")
        resp = gpt.generate(msg, **prompt_config)
        bot.reply_to(reply_to, resp)
        logger.info(f"[{chat if chat else 'Private'} | Bot]: {resp}")

    @bot.message_handler(func=lambda m: m.text.startswith('#bot '), content_types=['text'])
    def handle_hashtag(message: types.Message):
        chat = message.chat.title
        sender = message.from_user.username
        msg = message.text[5:]
        chatting(chat, sender, msg, message)

    @bot.message_handler(func=lambda m: m.reply_to_message and m.reply_to_message.from_user.id == bot.get_me().id, content_types=['text'])
    def handle_reply(message: types.Message):
        chat = message.chat.title
        sender = message.from_user.username
        msg = message.text
        chatting(chat, sender, msg, message)

    try:
        bot.infinity_polling(skip_pending=True, timeout=200,
                            long_polling_timeout=200)
    except KeyboardInterrupt:
        logger.info("Killed by KeyboardInterrupt")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    try:
        logger.info("Starting...")
        Bot()
    except KeyboardInterrupt:
        logger.info("Killed by KeyboardInterrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
