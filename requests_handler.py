from configurations import configurations
from time import sleep
from flask_app import Job
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS

import inspect
import asyncio
import trello
import discordBot

config = configurations.get_config()
trelloManager = trello.trelloManager(configurations.get_config())
engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)
Session = sessionmaker(bind = engine, expire_on_commit = False)

def find_pending_job():
    with Session.begin() as session:
        queue = session.query(Job)
        return queue.first()

async def process_job(job):
    endpoint_dispatch_table = {
        "/githubPullRequest": process_github_job
        , "/trelloMovedToBoard": process_trello_job
    }

    if not job.endpoint in endpoint_dispatch_table:
        print(f"Endpoint {job.endpoint} not defined.")
        return

    if inspect.iscoroutinefunction(target_function := endpoint_dispatch_table[job.endpoint]):
        await target_function(job.payload)

    else:
        target_function(job.payload)

    with Session.begin() as session:
        session.query(Job).filter_by(id = job.id).delete()
        session.commit()

    return

async def process_github_job(payload):
    configurations.reload_config()

    if "pull_request" not in payload:
        return

    if payload["pull_request"]["merged"] == True:
        pullReqUserID = payload["pull_request"]["user"]["id"]
        pullReqTitle = payload["pull_request"]["title"]
        pullReqURL = payload["pull_request"]["html_url"]
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

    return

def process_trello_job(payload):
    configurations.reload_config()

    if "listAfter" not in payload["action"]["data"]:
        return

    if isUpdateCard(payload) and isMovedToReviewList(payload, config):
        cardID = payload["action"]["data"]["card"]["id"]
        votedMembers = trelloManager.getVotedMembers(cardID)
        for member in votedMembers:
            if find_member_by_trello_id(member, config):
                user = config["users"][find_member_by_trello_id(member, config)]
                trelloManager.clearVote(cardID, member["id"], user["trelloKey"], user["trelloToken"])

    return

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

async def main():
    while True:
        if not (job := find_pending_job()):
            sleep(1)
            continue

        await process_job(job)

def init_requests_handler():
    asyncio.run(main())
