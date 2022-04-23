from aiohttp import web
from concurrent.futures import ProcessPoolExecutor
import discordBot
import asyncio
import yaml
import trello

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

routes = web.RouteTableDef()

@routes.post("/githubPullRequest")
async def fetchDetails(request):
	data = await request.json()
	
	if data["pull_request"]["merged"] == True:
		message_string = discordBot.createMessage(data, config)
		await discordBot.sendMessage(config, message_string)
		
		responses = trello.getCardsFromList(config["trelloMoveFromListID"], config)
		for response in responses:
			desc = trello.getCardDesc(response["id"], config)
			print(data["pull_request"]["html_url"])
			print(desc["_value"])
			if trello.findCard(data["pull_request"]["html_url"], desc["_value"]) == True:
				trello.moveCardToList(response["id"], config)

	return web.json_response(data)

@routes.head("/trelloMovedToBoard")
async def initWebhook(request):

	return web.json_response()

@routes.post("/trelloMovedToBoard")
async def movedToBoard(request):
	data = await request.json()

	try:
		if data["action"]["type"] == "updateCard" and data["action"]["data"]["listAfter"]["id"] == config["trelloWatchListID"]:
			print("Movement detected.")

			cardID = data["action"]["data"]["card"]["id"]
			responses = trello.getVotedMembers(cardID, config)
			for response in responses:
				trello.clearVotes(cardID, config, response["id"])
	except KeyError:
		pass

	return web.json_response(data)

def run_server():
	app = web.Application()
	app.add_routes(routes)
	web.run_app(app)

def run_bot():
	discordBot.bot.run()

if __name__ == "__main__":
	executor = ProcessPoolExecutor(2)
	loop = asyncio.new_event_loop()
	dc_bot = loop.run_in_executor(executor, run_bot)
	server = loop.run_in_executor(executor, run_server)
	
	try:
		trello.initWebhook(config)
		loop.run_forever()
	except KeyboardInterrupt:
		print("Exiting...")