import requests
import json
import re
import yaml

with open('config.yaml', 'r+') as f:
	config = yaml.safe_load(f)

def getCardsFromList(id):
	url = f"https://api.trello.com/1/lists/{id}/cards"

	headers = {"Accept": "application/json"}

	query = {'key': config["mainUserAPIKey"],
			 'token': config["mainUserToken"]}

	response = requests.request("GET", url, headers=headers, params=query)

	return response.json()

def getCardDesc(id):
	url = f"https://api.trello.com/1/cards/{id}/desc"

	headers = {"Accept": "application/json"}

	query = {'key': config["mainUserAPIKey"],
			 'token': config["mainUserToken"]}

	response = requests.request("GET", url, headers=headers, params=query)

	return response.json()

def findCard(htmlURL, desc):
	regex = r"PULL REQUEST: http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
	urls = re.findall(regex, desc)
	target = f"PULL REQUEST: {htmlURL}"
	for url in urls:
		if url == target:
			print("Target found.")
			return True

def moveCardToList(id):
	url = f"https://api.trello.com/1/cards/{id}"

	headers = {"Accept": "application/json"}

	query = {'key': config["mainUserAPIKey"], 
			 'token': config["mainUserToken"],
			 'idList': config["trelloMoveToListID"]}

	response = requests.request("PUT", url, headers=headers, params=query)

	print("Move was successful.")

def getVotedMembers(id):
	url = f"https://api.trello.com/1/cards/{id}/membersVoted"

	query = {'key': config["mainUserAPIKey"], 
			 'token': config["mainUserToken"]}

	response = requests.request("GET", url, params=query)

	return response.json()

def clearVotes(id, idMember):
	url = f"https://api.trello.com/1/cards/{id}/membersVoted/{idMember}"

	query = {'key': config["trelloAPIKeyMapping"][idMember],
			 'token': config["trelloTokenMapping"][idMember]}
	
	response = requests.request("DELETE", url, params=query)

def initWebhook():
	url = "https://api.trello.com/1/webhooks"

	headers = {"Accept": "application/json"}

	query = {'callbackURL': 'https://8363-218-111-14-86.ngrok.io/trelloMovedToBoard',
   			 'idModel': config["trelloWatchListID"],
   			 'key': config["mainUserAPIKey"],
	   		 'token': config["mainUserToken"]
	}

	response = requests.request("POST", url, headers=headers, params=query)

	print("Webhook initialized.")	