# otacon-bot/database/tortoise_config.py

import os

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DATABASE_URL")
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "database.models"],
            "default_connection": "default",
        }
    }
}
