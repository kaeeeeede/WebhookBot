import hikari
import lightbulb
import yaml

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

bot = lightbulb.BotApp(token = config['DISCORD_TOKEN'])

def createMessage(data, config):
	id_string = data["pull_request"]["user"]["id"]
	user_id = str(config['gitDiscordMapping'].get(id_string))

	if not user_id == "None":
		message_string = "<@" + user_id + ">.\n" + 'Pull request titled "' + data["pull_request"]["title"] + '" has been merged.\n' + "Link: " + data["pull_request"]["html_url"]

	else:
		message_string = 'Pull request titled "' + data["pull_request"]["title"] + '" has been merged.\n' + "Link: " + data["pull_request"]["url"]
		print("PULL REQUEST MERGED WITHOUT MATCHING DISCORD ID")
		print("User ID: " + str(data["pull_request"]["user"]["id"]))
		print("Pull request title: " + data["pull_request"]["title"])
		print("Pull request link: " + data["pull_request"]["html_url"])

	return message_string

async def sendMessage(config, message_string):
	async with hikari.RESTApp().acquire(config.get('DISCORD_TOKEN'), hikari.TokenType.BOT) as client:
			await client.create_message(config.get('targetChannelID'), message_string)

	return