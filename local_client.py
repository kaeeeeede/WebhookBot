from configurations import configurations
from concurrent.futures import ProcessPoolExecutor
import asyncio
import discordBot
import trello
import webhook

def run_server():
	app = webhook.init_webapp()
	webhook.web.run_app(app)

def run_bot():
	discordBot.bot.run()

if __name__ == "__main__":
	executor = ProcessPoolExecutor(2)
	loop = asyncio.new_event_loop()
	dc_bot = loop.run_in_executor(executor, run_bot)
	server = loop.run_in_executor(executor, run_server)

	try:
		config = configurations.get_config()
		trelloManager = trello.trelloManager(config)
		trelloManager.initWebhook(config["trelloReviewListID"], config["hostURL"])
		loop.run_forever()
	except KeyboardInterrupt:
		print("Exiting...")
