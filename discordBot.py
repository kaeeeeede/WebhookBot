import hikari
import lightbulb
import yaml

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

bot = lightbulb.BotApp(token = config['DISCORD_TOKEN'])

def createMessage(pullReqUserID, discordUserID, pullReqTitle, pullReqURL):
	if not discordUserID == "None":
		return f"<@{discordUserID}>.\nPull request titled \"{pullReqTitle}\" has been merged.\nLink: {pullReqURL}"

	print("PULL REQUEST MERGED WITHOUT MATCHING DISCORD ID")
	print(f"User ID: {pullReqUserID}")
	print(f"Pull request title: {pullReqTitle}")
	print(f"Pull request link: {pullReqURL}")
	
	return f"Pull request titled \"{pullReqTitle}\" has been merged.\nLink: {pullReqURL}"

async def sendMessage(message_string, discordToken, targetChannelID):
	async with hikari.RESTApp().acquire(discordToken, hikari.TokenType.BOT) as client:
			await client.create_message(targetChannelID, message_string)

	return
