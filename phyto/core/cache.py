from databases import Database


class Cache:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def load(self):
        await self.db.connect()

    async def unload(self):
        await self.db.disconnect()
