import sqlite3, aiosqlite, aiohttp
from contextlib import closing


class UserLevelsDb:
    TABLE_PARAMS = {
        "user_id": 'INT PRIMARY KEY NOT NULL UNIQUE',
        "total_messages": 'INT',
        "user_level": 'INT',
    }

    def __init__(self, dbpath, tablename):
        self.path = dbpath
        self._default_table = tablename

    def create_table(self):
        """Как пользоваться? (атрибут _default_table -  название таблицы', TABLE_PARAMS - словарь содержит поля и тип данных
        id="INT PRIMARY KEY", source='TEXT', recieve_time= 'INT' итд)"""
        params = ''
        for key, val in self.TABLE_PARAMS.items():
            params += f'{key} {val.upper()}, '
        params = params.rstrip(', ')
        sql_cmd = f"CREATE TABLE IF NOT EXISTS {self._default_table} ({params})"
        try:
            with closing(sqlite3.connect(self.path)) as connection:
                cursor = connection.cursor()
                cursor.execute(sql_cmd)
                cursor.close()
                connection.commit()
            return True
        except Exception as e:
            return e

    async def create_user(self, user_id):
        sql_cmd = f"INSERT INTO {self._default_table} VALUES (?,?,?)"
        total_messages = 1
        user_level = 1
        try:
            async with aiosqlite.connect(self.path) as connection:
                cursor = await connection.cursor()
                await cursor.execute(sql_cmd, (user_id, total_messages, user_level))
                await connection.commit()
                return True
        except Exception :
            await connection.rollback()
            return False

    async def update_params(self, user_id, **kwargs):

        try:
            for param, value in kwargs.items():
                sql_cmd = f'UPDATE {self._default_table} SET "{param}" = ? WHERE "user_id" = ?'
                async with aiosqlite.connect(self.path) as connection:
                    cursor = await connection.cursor()
                    await cursor.execute(sql_cmd, (value, user_id))
                    await connection.commit()
            return True
        except Exception :
            await connection.rollback()
            return False

    async def get_user_info(self, user_id):

        sql_cmd = f"SELECT * FROM {self._default_table} WHERE user_id =?"
        try:
            async with aiosqlite.connect(self.path) as connection:
                cursor = await connection.cursor()
                await cursor.execute(sql_cmd, (user_id,))
                result = await cursor.fetchone()
            if result:
                return result[1], result[2]
        except:
            return None


class Giphy:

    @staticmethod
    async def search(text):
        payload = {
            'api_key': 'UkTdvyjJSJG5B6SgkoAmbaTQn7Ed8zRC',
            'q': text,
            'limit': 10,

        }
        async with aiohttp.ClientSession() as session:
            url = 'https://api.giphy.com/v1/gifs/search'
            async with session.get(url, params=payload) as resp:
                response = await resp.json()
        return Giphy._parse_results(response, 1)

    @staticmethod
    def _parse_results(response, limit):
        output = []
        try:
            items = response.get('data', [])[:limit]
            for item in items:
                output.append(item['images']['downsized']['url'])
            return output
        except Exception as e:
            print(e)
            return []


