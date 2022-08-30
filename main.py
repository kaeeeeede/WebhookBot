from concurrent.futures import ProcessPoolExecutor
import asyncio

import discordBot
import requests_handler

if __name__ == "__main__":
    executor = ProcessPoolExecutor(2)
    loop = asyncio.new_event_loop()
    discord_bot = loop.run_in_executor(executor, discordBot.init_bot)
    req_handler = loop.run_in_executor(executor, requests_handler.init_requests_handler)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print("Exiting.")
