import asyncio

from way_bill.bot import WayBillBot


async def main():
    bot = WayBillBot()
    await bot.init_bot()
    await bot.run()


asyncio.run(main())
