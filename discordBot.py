from hikari.messages import MessageFlag
from configurations import configurations
from yaml.representer import Representer
from collections import defaultdict
from copy import copy
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
@lightbulb.option("name", "Enter the user's name")
@lightbulb.option("discordid", "Enter the user's Discord ID")
@lightbulb.option("githubid", "Enter the user's GitHub ID", type = int, default = "None")
@lightbulb.option("trelloid", "Enter the user's Trello ID", default = "None")
@lightbulb.option("trellokey", "Enter the user's Trello API Key", default = "None")
@lightbulb.option("trellotoken", "Enter the user's Trello Token", default = "None")
@lightbulb.command("insertuser", "Insert a new user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def insertUser(ctx):
	configurations.reload_config()

	if config.get("users"):
		if get_user_by_discord_id(ctx.options.discordid):
			await ctx.respond("User already exists.", flags = MessageFlag.EPHEMERAL)

			return

		else:
			new_user_id = list(config["users"])[-1] + 1

	else:
		new_user_id = 1

	temp_dict = {"name": ctx.options.name
				, "discordID": ctx.options.discordid}

	temp_dict.update(create_dict(ctx.options.githubid, ctx.options.discordid, ctx.options.trelloid, ctx.options.trellokey, ctx.options.trellotoken))
	config["users"][new_user_id] = temp_dict

	with open('config.yaml', 'w') as f:
		f.write(yaml.dump(config, sort_keys = False, default_style = ""))

	await ctx.respond("User added.", flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("currentdiscordid", "Enter the user's current Discord ID")
@lightbulb.option("githubid", "Enter the user's GitHub ID", type = int, default = "None")
@lightbulb.option("newdiscordid", "Enter the user's new Discord ID", default = "None")
@lightbulb.option("trelloid", "Enter the user's Trello ID", default = "None")
@lightbulb.option("trellokey", "Enter the user's Trello API Key", default = "None")
@lightbulb.option("trellotoken", "Enter the user's Trello Token", default = "None")
@lightbulb.command("updateuser", "Insert a new user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def updateUser(ctx):
	configurations.reload_config()

	if not get_user_by_discord_id(ctx.options.currentdiscordid):
		await ctx.respond("User not found.", flags = MessageFlag.EPHEMERAL)

		return

	temp_dict = create_dict(ctx.options.githubid, ctx.options.newdiscordid, ctx.options.trelloid, ctx.options.trellokey, ctx.options.trellotoken)
	user = config["users"][get_user_by_discord_id(ctx.options.currentdiscordid)]
	user.update(temp_dict)

	if ctx.options.newdiscordid == "None":
		message = get_user_details(get_user_by_discord_id(ctx.options.currentdiscordid))

	else:
		message = get_user_details(get_user_by_discord_id(ctx.options.newdiscordid))

	with open('config.yaml', 'w') as f:
		f.write(yaml.dump(config, sort_keys = False, default_style = ""))

	await ctx.respond("User updated.", flags = MessageFlag.EPHEMERAL)
	await ctx.respond(message, flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("discordid", "Enter the user's Discord ID")
@lightbulb.command("deleteuser", "Delete a user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def deleteUser(ctx):
	configurations.reload_config()

	if not get_user_by_discord_id(ctx.options.discordid):
		await ctx.respond("User not found.", flags = MessageFlag.EPHEMERAL)

		return

	user = get_user_by_discord_id(ctx.options.discordid)
	config["users"].pop(user)

	with open('config.yaml', 'w') as f:
		f.write(yaml.dump(config, sort_keys = False, default_style = ""))

	await ctx.respond("User deleted.", flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("discordid", "Enter the user's Discord ID")
@lightbulb.command("showuser", "Show the details of a user", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def showUser(ctx):
	configurations.reload_config()

	if not get_user_by_discord_id(ctx.options.discordid):
		await ctx.respond("User not found.", flags = MessageFlag.EPHEMERAL)

		return

	message = get_user_details(get_user_by_discord_id(ctx.options.discordid))

	await ctx.respond(message, flags = MessageFlag.EPHEMERAL)

def get_user_by_discord_id(targetID):
	for user in config["users"]:
		if config["users"][user].get("discordID") == targetID:
			return user

def get_user_details(user):
	message = f"Details of user {user}\n"

	for key in config["users"][user]:
		value = config["users"][user][key]
		message = message + f"{key}: {value}\n"

	return message

def create_dict(githubID, discordID, trelloID, trelloKey, trelloToken):
	temp_dict = {"githubID": githubID
				, "discordID": discordID
				, "trelloID": trelloID
				, "trelloKey": trelloKey
				, "trelloToken": trelloToken}

	temp_dict = {x: y for (x, y) in temp_dict.items() if y != "None"}

	return temp_dict

def init_bot():
    bot.run()
