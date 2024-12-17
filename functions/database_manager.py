import aiosqlite

from config import DATABASE


class DatabaseManager:
    def __init__(self):
        self.database = DATABASE

    async def _execute(self, query, params=(), fetch=None):
        async with aiosqlite.connect(self.database) as conn:
            cursor = await conn.execute(query, params)
            if fetch == "one":
                result = await cursor.fetchone()
            elif fetch == "all":
                result = await cursor.fetchall()
            else:
                result = None
            await conn.commit()
            return result

    async def initialize(self):
        await self._execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                notify_by_minutes INTEGER
            );
        """)
        await self._execute("""
            CREATE TABLE IF NOT EXISTS usersLocations2 (
                userloc_id INTEGER PRIMARY KEY, 
                user_id INTEGER, 
                turn INTEGER, 
                tag_name TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
        """)
        await self._execute("""
            CREATE TABLE IF NOT EXISTS support_requests (
                request_message_id INTEGER PRIMARY KEY, 
                user_id INTEGER
            );
        """)

    async def get_users(self):
        return await self._execute("SELECT * FROM users", fetch="all")

    async def add_user(self, user_id):
        try:
            await self._execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        except aiosqlite.IntegrityError:
            pass

    async def get_user_locations(self, user_id):
        rows = await self._execute(
            "SELECT tag_name, turn, userloc_id FROM usersLocations2 WHERE user_id = ?",
            (user_id,),
            fetch="all"
        )
        return [{"location": row[0], "turn": row[1], "id": row[2]} for row in rows]

    async def add_user_location(self, user_id, turn, location_tag):
        await self._execute(
            "INSERT INTO usersLocations2 (user_id, turn, tag_name) VALUES (?, ?, ?)",
            (user_id, turn, location_tag)
        )

    async def delete_user_location(self, location_id):
        await self._execute("DELETE FROM usersLocations2 WHERE userloc_id = ?", (location_id,))

    async def get_user_notification_time(self, user_id):
        row = await self._execute(
            "SELECT notify_by_minutes FROM users WHERE user_id = ?",
            (user_id,),
            fetch="one"
        )
        return row[0] if row else None

    async def set_notification_time_for_user(self, user_id, notify_by):
        await self._execute(
            "UPDATE users SET notify_by_minutes = ? WHERE user_id = ?",
            (notify_by, user_id)
        )

    async def add_support_request(self, user_id, request_message_id):
        await self._execute(
            "INSERT INTO support_requests (request_message_id, user_id) VALUES (?, ?)",
            (request_message_id, user_id)
        )

    async def get_user_id_by_support_request_message(self, request_message_id):
        row = await self._execute(
            "SELECT user_id FROM support_requests WHERE request_message_id = ?",
            (request_message_id,),
            fetch="one"
        )
        return row[0] if row else None


db = DatabaseManager()
