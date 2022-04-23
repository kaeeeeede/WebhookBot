import requests
import json
import re

def getCardsFromList(id, config):
	url = f"https://api.trello.com/1/lists/{id}/cards"

	headers = {"Accept": "application/json"}

	query = {
		'key': config["mainUserAPIKey"],
	    'token': config["mainUserToken"]}

	response = requests.request("GET", url, headers=headers, params=query)

	return response.json()

def getCardDesc(id, config):
	url = f"https://api.trello.com/1/cards/{id}/desc"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': config["mainUserAPIKey"],
	   'token': config["mainUserToken"]}

	response = requests.request("GET", url, headers=headers, params=query)

	return response.json()

def findCard(targetURL, desc):
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	urls = re.findall(regex, desc)
	for url in urls:
		if url == targetURL:
			print("Target found.")
			return True

def moveCardToList(id, config):
	url = f"https://api.trello.com/1/cards/{id}"

	headers = {"Accept": "application/json"}

	query = {'key': config["mainUserAPIKey"],
			 'token': config["mainUserToken"],
			 'idList': config["trelloMoveToListID"]}

	response = requests.request("PUT", url, headers=headers, params=query)

	print("Move was successful.")

def getVotedMembers(id, config):
	url = f"https://api.trello.com/1/cards/{id}/membersVoted"

	query = {
	   'key': config["mainUserAPIKey"],
	   'token': config["mainUserToken"]
	}

	response = requests.request(
	   "GET",
	   url,
	   params=query
	)

	return response.json()

def clearVotes(id, config, idMember):
	url = f"https://api.trello.com/1/cards/{id}/membersVoted/{idMember}"

	print(config["trelloAPIKeyMapping"][idMember], " ", config["trelloTokenMapping"][idMember])

	query = {
	   'key': config["trelloAPIKeyMapping"][idMember],
	   'token': config["trelloTokenMapping"][idMember]
	}

	response = requests.request(
	   "DELETE",
	   url,
	   params=query
	)

	return

def initWebhook(config):
	url = "https://api.trello.com/1/webhooks"

	headers = {"Accept": "application/json"}

	query = {'callbackURL': 'https://77bb-218-111-14-86.ngrok.io/trelloMovedToBoard',
   			 'idModel': config["trelloWatchListID"],
   			 'key': config["mainUserAPIKey"],
	   		 'token': config["mainUserToken"]
	}

	response = requests.request("POST", url, headers=headers, params=query)

	print("Webhook initialized.")	