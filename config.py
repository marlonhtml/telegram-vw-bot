from os import getenv
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("TELEGRAM_TOKEN").strip()
VIMEtoken = getenv("ACCESS_TOKEN").strip()
