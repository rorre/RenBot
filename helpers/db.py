import aiosqlite, sqlite3
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
        message_id integer,
        status integer
    ); """)
    db.commit()
    db.close()