from aiohttp import web
from concurrent.futures import ProcessPoolExecutor
import discordBot
import asyncio
import yaml
import trello

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

routes = web.RouteTableDef()
trelloManager = trello.trelloManager(config)

@routes.post("/githubPullRequest")
async def fetchDetails(request):
	data = await request.json()
	
	if "pull_request" not in data:
		return web.json_response(data) 

	if data["pull_request"]["merged"] == True:
		pullReqUserID = data["pull_request"]["user"]["id"]
		discordUserID = str(config['gitDiscordMapping'].get(pullReqUserID))
		pullReqTitle = data["pull_request"]["title"]
		pullReqURL = data["pull_request"]["html_url"]
		discordToken = config.get('DISCORD_TOKEN')
		targetChannelID = config.get('targetChannelID')

		message_string = discordBot.createMessage(pullReqUserID, discordUserID, pullReqTitle, pullReqURL)
		await discordBot.sendMessage(message_string, discordToken,  targetChannelID)
		
		cards = trelloManager.getCardsFromList(config["trelloMoveFromListID"])
		for card in cards:
			desc = trelloManager.getCardDesc(card["id"])
			if trelloManager.urlExistsIn(desc["_value"], pullReqURL) == True:
				trelloManager.moveCardToList(card["id"], config["trelloMoveToListID"])

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

	if isUpdateCard(data) and isMovedToReviewList(data):
		cardID = data["action"]["data"]["card"]["id"]
		votedMembers = trelloManager.getVotedMembers(cardID)
		for member in votedMembers:
			if member["id"] in config["trelloMapping"]: 
				trelloManager.clearVote(cardID, member["id"])

	return web.json_response(data)

def run_server():
	app = web.Application()
	app.add_routes(routes)
	web.run_app(app)

def run_bot():
	discordBot.bot.run()

def isUpdateCard(data):
	if data["action"]["type"] == "updateCard":
		return True

	return False

def isMovedToReviewList(data):
	if data["action"]["data"]["listAfter"]["id"] == config["trelloReviewListID"]:
		return True

	return False

if __name__ == "__main__":
	executor = ProcessPoolExecutor(2)
	loop = asyncio.new_event_loop()
	dc_bot = loop.run_in_executor(executor, run_bot)
	server = loop.run_in_executor(executor, run_server)
	
	try:
		trelloManager.initWebhook(config["trelloReviewListID"], config["hostURL"])
		loop.run_forever()
	except KeyboardInterrupt:
		print("Exiting...")
