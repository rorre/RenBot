import os
import config
from bot import bot

if not os.path.exists(config.database_name):
    from helpers import db
    db.initialize_db()

bot.run(config.token)