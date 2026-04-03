import os

os.environ.setdefault("WPD_APP_TITLE", "Danish Politics Data")
os.environ.setdefault("WPD_EXPOSE_COUNTRIES", "denmark")

from engine_app import *  # noqa: F401,F403
