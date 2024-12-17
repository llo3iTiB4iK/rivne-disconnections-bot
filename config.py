import os
import pytz
from dotenv import load_dotenv

load_dotenv()

TEST_ENV = True  # True for test environment, False for production environment
BOT_TOKEN = os.getenv("TEST_BOT_TOKEN" if TEST_ENV else "PROD_BOT_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

DATABASE = 'user_data.db'
"""
When deploying bot on platforms, where multithreading is disabled (im my case, PythonAnywhere), aiosqlite connection to
database fails, because it is created using Thread() class. In this case, set this flag to False.
"""
MULTI_THREADED = True


DISCONNECTIONS_URL = "https://www.roe.vsei.ua/disconnections"
NUM_TURNS = 12

DISCONNECTIONS_CHECK_INTERVAL = 5
NOTIFICATION_CHECK_INTERVAL = 5

TIMEZONE = pytz.timezone('Europe/Kyiv')
