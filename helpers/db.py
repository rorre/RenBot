import sqlite3
import aiosqlite
import config


async def query(q):
    async with aiosqlite.connect(config.database_name) as db:
        if type(q) is str:
            cursor = await db.execute(q)
        elif type(q) in [list, tuple]:
            cursor = await db.execute(q[0], q[1])
        async_res = await cursor.fetchall()
        await db.commit()
        return async_res


def initialize_db():
    db = sqlite3.connect(config.database_name)
    db.execute("""CREATE TABLE requests (
        id integer PRIMARY KEY,
        requester_uid integer NOT NULL,
        mapset_url text NOT NULL,
        accepted integer,
        reason text,
        message_id text,
        status integer
    ); """)
    db.execute("""CREATE TABLE users (
        uid integer NOT NULL UNIQUE,
        osu_uid integer NOT NULL UNIQUE
    );""")
    db.commit()
    db.close()
