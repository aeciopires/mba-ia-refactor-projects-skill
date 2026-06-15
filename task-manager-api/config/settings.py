import os

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

VALID_TASK_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
TASK_PRIORITY_MIN = 1
TASK_PRIORITY_MAX = 5
