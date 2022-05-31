from aiohttp import web
from configurations import configurations
import discordBot
import trello

config = configurations.get_config()
routes = web.RouteTableDef()
trelloManager = trello.trelloManager(configurations.get_config())

@routes.post("/githubPullRequest")
async def fetchDetails(request):
	configurations.reload_config()
	data = await request.json()
	
	if "pull_request" not in data:
		return web.json_response(data) 

	if data["pull_request"]["merged"] == True:
		pullReqUserID = data["pull_request"]["user"]["id"]
		pullReqTitle = data["pull_request"]["title"]
		pullReqURL = data["pull_request"]["html_url"]
		discordToken = config.get('DISCORD_TOKEN')
		targetChannelID = config.get('targetChannelID')

		if not config["users"].get(find_user_by_github_id(pullReqUserID, config)) == None:
			discordUserID = config["users"][find_user_by_github_id(pullReqUserID, config)]["discordID"]

		else:
			discordUserID = "None"

		message_string = discordBot.createMessage(pullReqUserID, discordUserID, pullReqTitle, pullReqURL)
		await discordBot.sendMessage(message_string, discordToken, targetChannelID)
		
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
	configurations.reload_config()
	data = await request.json()

	if "listAfter" not in data["action"]["data"]:
		return web.json_response(data)

	if isUpdateCard(data) and isMovedToReviewList(data, config):
		cardID = data["action"]["data"]["card"]["id"]
		votedMembers = trelloManager.getVotedMembers(cardID)
		for member in votedMembers:
			if find_member_by_trello_id(member, config):
				user = config["users"][find_member_by_trello_id(member, config)]
				trelloManager.clearVote(cardID, member["id"], user["trelloKey"], user["trelloToken"])

	return web.json_response(data)

def find_member_by_trello_id(member, config):
	for user in config["users"]:
		if member["id"] == config["users"][user].get("trelloID"):
			return user

def find_user_by_github_id(targetID, config):
	for user in config["users"]:
		if config["users"][user].get("githubID") == targetID:
			return user

def isMovedToReviewList(data, config):
	if data["action"]["data"]["listAfter"]["id"] == config["trelloReviewListID"]:
		return True

	return False

def isUpdateCard(data):
	if data["action"]["type"] == "updateCard":
		return True

	return False

def init_webapp():
	app = web.Application()
	app.add_routes(routes)

	return app
