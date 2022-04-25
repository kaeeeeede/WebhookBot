import requests
import json
import re

class trelloManager:
	def __init__(self, mainUserAPIKey, mainUserToken):
		self.mainUserAPIKey = mainUserAPIKey
		self.mainUserToken = mainUserToken

	def getCardsFromList(self, listID):
		url = f"https://api.trello.com/1/lists/{listID}/cards"

		headers = {"Accept": "application/json"}

		query = {'key': self.mainUserAPIKey,
				 'token': self.mainUserToken}

		response = requests.request("GET", url, headers=headers, params=query)

		return response.json()

	def getCardDesc(self, cardID):
		url = f"https://api.trello.com/1/cards/{cardID}/desc"

		headers = {"Accept": "application/json"}

		query = {'key': self.mainUserAPIKey,
				 'token': self.mainUserToken}

		response = requests.request("GET", url, headers=headers, params=query)

		return response.json()

	def findURL(self, pullRequestURL, desc):
		regex = rf"PULL REQUEST: {pullRequestURL}"
		if re.findall(regex, desc):
			return True

	def moveCardToList(self, cardID, trelloMoveToListID):
		url = f"https://api.trello.com/1/cards/{cardID}"

		headers = {"Accept": "application/json"}

		query = {'key': self.mainUserAPIKey, 
				 'token': self.mainUserToken,
				 'idList': trelloMoveToListID}

		response = requests.request("PUT", url, headers=headers, params=query)

	def getVotedMembers(self, cardID):
		url = f"https://api.trello.com/1/cards/{cardID}/membersVoted"

		query = {'key': self.mainUserAPIKey, 
				 'token': self.mainUserToken}

		response = requests.request("GET", url, params=query)

		return response.json()

	def clearVote(self, cardID, memberID, memberAPIKey, memberToken):
		url = f"https://api.trello.com/1/cards/{cardID}/membersVoted/{memberID}"

		query = {'key': memberAPIKey,
				 'token': memberToken}
		
		response = requests.request("DELETE", url, params=query)

	def initWebhook(self, trelloWatchListID):
		url = "https://api.trello.com/1/webhooks"

		headers = {"Accept": "application/json"}

		query = {'callbackURL': 'https://4162-218-111-14-86.ngrok.io/trelloMovedToBoard',
	   			 'idModel': trelloWatchListID,
	   			 'key': self.mainUserAPIKey,
		   		 'token': self.mainUserToken
		}

		response = requests.request("POST", url, headers=headers, params=query)