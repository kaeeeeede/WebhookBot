import hikari
import lightbulb
import yaml

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

bot = lightbulb.BotApp(token = config['DISCORD_TOKEN'])

def createMessage(data):
	id_string = data["pull_request"]["user"]["id"]
	user_id = str(config['gitDiscordMapping'].get(id_string))

	title_string = data["pull_request"]["title"]
	html_string = data["pull_request"]["html_url"]

	if not user_id == "None":
		message_string = f"<@{user_id}>.\nPull request titled \"{title_string}\" has been merged.\nLink: {html_string}"

	else:
		message_string = f"Pull request titled \"{title_string}\" has been merged.\nLink: {html_string}"
		print("PULL REQUEST MERGED WITHOUT MATCHING DISCORD ID")
		print(f"User ID: {user_id}")
		print(f"Pull request title: {title_string}")
		print(f"Pull request link: {html_string}")

	return message_string

async def sendMessage(message_string):
	async with hikari.RESTApp().acquire(config.get('DISCORD_TOKEN'), hikari.TokenType.BOT) as client:
			await client.create_message(config.get('targetChannelID'), message_string)

	return