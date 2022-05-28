from hikari.messages import MessageFlag
from configurations import configurations
from yaml.representer import Representer
from collections import defaultdict
import hikari
import lightbulb
import yaml

representer = yaml.add_representer(defaultdict, Representer.represent_dict)
config = configurations.get_config()

bot = lightbulb.BotApp(token = config["DISCORD_TOKEN"])

def createMessage(pullReqUserID, discordUserID, pullReqTitle, pullReqURL):
	if not discordUserID == "None":
		return f"<@{discordUserID}>\nPull request titled \"{pullReqTitle}\" has been merged.\nLink: {pullReqURL}"

	print("PULL REQUEST MERGED WITHOUT MATCHING DISCORD ID")
	print(f"User ID: {pullReqUserID}")
	print(f"Pull request title: {pullReqTitle}")
	print(f"Pull request link: {pullReqURL}")
	
	return f"Pull request titled \"{pullReqTitle}\" has been merged.\nLink: {pullReqURL}"

async def sendMessage(message_string, discordToken, targetChannelID):
	async with hikari.RESTApp().acquire(discordToken, hikari.TokenType.BOT) as client:
			await client.create_message(targetChannelID, message_string)

	return

@bot.command
@lightbulb.option("userid", "Enter the user's ID", type = int)
@lightbulb.option("name", "Enter the user's name")
@lightbulb.option("githubid", "Enter the user's GitHub ID", default = "None")
@lightbulb.option("discordid", "Enter the user's Discord ID", default = "None")
@lightbulb.option("trelloid", "Enter the user's Trello ID", default = "None")
@lightbulb.option("trellokey", "Enter the user's Trello API Key", default = "None")
@lightbulb.option("trellotoken", "Enter the user's Trello Token", default = "None")
@lightbulb.command("insertuser", "Insert a new user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def insertUser(ctx):
	configurations.reload_config()
	temp_dict = {}

	temp_dict["name"] = ctx.options.name

	if not ctx.options.githubid == "None":
		temp_dict["githubID"] = ctx.options.githubid

	if not ctx.options.discordid == "None":
		temp_dict["discordID"] = ctx.options.discordid

	if not ctx.options.trelloid == "None":
		temp_dict["trelloID"] = ctx.options.trelloid

	if not ctx.options.trellokey == "None":
		temp_dict["trelloKey"] = ctx.options.trellokey

	if not ctx.options.trellotoken == "None":
		temp_dict["trelloToken"] = ctx.options.trellotoken

	config["users"][ctx.options.userid] = temp_dict

	with open('config.yaml', 'w') as f:
		f.write(yaml.dump(config, sort_keys = False, default_style = ""))

	await ctx.respond("User added.", flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("userid", "Enter the user's ID", type = int)
@lightbulb.option("githubid", "Enter the user's GitHub ID", default = "None")
@lightbulb.option("discordid", "Enter the user's Discord ID", default = "None")
@lightbulb.option("trelloid", "Enter the user's Trello ID", default = "None")
@lightbulb.option("trellokey", "Enter the user's Trello API Key", default = "None")
@lightbulb.option("trellotoken", "Enter the user's Trello Token", default = "None")
@lightbulb.command("updateuser", "Insert a new user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def updateUser(ctx):
	configurations.reload_config()
	if not user_exists_in_config(ctx.options.userid):
		await ctx.respond("User not found.")

		return

	if not ctx.options.githubid == "None":
		config["users"][ctx.options.userid]["githubID"] = ctx.options.githubid

	if not ctx.options.discordid == "None":
		config["users"][ctx.options.userid]["discordID"] = ctx.options.discordid

	if not ctx.options.trelloid == "None":
		config["users"][ctx.options.userid]["trelloID"] = ctx.options.trelloid

	if not ctx.options.trellokey == "None":
		config["users"][ctx.options.userid]["trelloKey"] = ctx.options.trellokey

	if not ctx.options.trellotoken == "None":
		config["users"][ctx.options.userid]["trelloToken"] = ctx.options.trellotoken

	with open('config.yaml', 'w') as f:
		f.write(yaml.dump(config, sort_keys = False, default_style = ""))

	await ctx.respond("User updated.", flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("userid", "Enter the user's ID", type = int)
@lightbulb.command("getuser", "Get the details of a user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def getUser(ctx):
	configurations.reload_config()
	
	if not user_exists_in_config(ctx.options.userid):
		await ctx.respond("User not found.", flags = MessageFlag.EPHEMERAL)

		return

	message = get_user_details(ctx.options.userid)

	await ctx.respond(message, flags = MessageFlag.EPHEMERAL)

def user_exists_in_config(targetID):
	for user in config["users"]:
		if user == targetID:
			return True

	return False

def get_user_details(user):
	message = f"Details of user {user}\n"

	for key in config["users"][user]:
		value = config["users"][user][key]
		message = message + f"{key}: {value}\n"

	return message
