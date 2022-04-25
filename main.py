from aiohttp import web
from concurrent.futures import ProcessPoolExecutor
import discordBot
import asyncio
import yaml
import trello

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

routes = web.RouteTableDef()
trelloManager = trello.trelloManager(config["mainUserAPIKey"], config["mainUserToken"])

@routes.post("/githubPullRequest")
async def fetchDetails(request):
	data = await request.json()
	
	if "pull_request" not in data:
		return web.json_response(data) 

	if data["pull_request"]["merged"] == True:
		message_string = discordBot.createMessage(data, config)
		await discordBot.sendMessage(message_string, config)
		
		responses = trelloManager.getCardsFromList(config["trelloMoveFromListID"])
		for response in responses:
			desc = trelloManager.getCardDesc(response["id"])
			if trelloManager.findURL(data["pull_request"]["html_url"], desc["_value"]) == True:
				trelloManager.moveCardToList(response["id"], config["trelloMoveToListID"])

		return web.json_response(data)

@routes.head("/trelloMovedToBoard")
async def initWebhook(request):
	print("Webhook initialized.")

	return web.json_response()

@routes.post("/trelloMovedToBoard")
async def movedToBoard(request):
	data = await request.json()

	if "listAfter" not in data["action"]["data"]:
		return web.json_response(data)

	if data["action"]["type"] == "updateCard" and data["action"]["data"]["listAfter"]["id"] == config["trelloWatchListID"]:
		cardID = data["action"]["data"]["card"]["id"]
		responses = trelloManager.getVotedMembers(cardID)
		for response in responses:
			if response["id"] in config["trelloMapping"]: 
				trelloManager.clearVote(cardID, response["id"], config["trelloMapping"][response["id"]][0], config["trelloMapping"][response["id"]][1])

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
		trelloManager.initWebhook(config["trelloWatchListID"])
		loop.run_forever()
	except KeyboardInterrupt:
		print("Exiting...")