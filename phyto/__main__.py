import asyncio

from . import Phyto


async def main():
    async with Phyto() as bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
