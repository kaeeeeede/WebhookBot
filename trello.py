import requests
import re
import copy

class trelloManager:
	def __init__(self, config):
		self.mainUserAPIKey = config["mainUserAPIKey"]
		self.mainUserToken = config["mainUserToken"]
		self.baseURL = "https://api.trello.com/1/"
		self.baseParams = {'key': self.mainUserAPIKey
						  ,'token': self.mainUserToken}

	def getCardsFromList(self, listID):
		url = f"https://api.trello.com/1/lists/{listID}/cards"

		headers = {"Accept": "application/json"}

		params = self.baseParams

		response = requests.request("GET", url, headers = headers, params = params)

		return response.json()

	def getCardDesc(self, cardID):
		url = f"{self.baseURL}cards/{cardID}/desc"

		headers = {"Accept": "application/json"}

		params = self.baseParams

		response = requests.request("GET", url, headers = headers, params = params)

		return response.json()

	def urlExistsIn(self, desc, pullRequestURL):
		regex = rf"PULL REQUEST\s?:\s?{pullRequestURL}"
		if re.search(regex, desc, re.IGNORECASE):
			return True

	def moveCardToList(self, cardID, listID):
		url = f"{self.baseURL}cards/{cardID}"

		headers = {"Accept": "application/json"}

		params = self.baseParams
		params['idList'] = listID

		response = requests.request("PUT", url, headers = headers, params = params)

	def getVotedMembers(self, cardID):
		url = f"{self.baseURL}cards/{cardID}/membersVoted"

		params = self.baseParams

		response = requests.request("GET", url, params = params)

		return response.json()

	def clearVote(self, cardID, memberID, memberKey, memberToken):
		url = f"{self.baseURL}cards/{cardID}/membersVoted/{memberID}"

		params = copy.deepcopy(self.baseParams)
		params['key'] = memberKey
		params['token'] = memberToken

		response = requests.request("DELETE", url, params = params)

	def initWebhook(self, trelloReviewListID, hostURL):
		url = f"{self.baseURL}webhooks"

		headers = {"Accept": "application/json"}

		params = self.baseParams
		params['callbackURL'] = f'{hostURL}/trelloMovedToBoard'
		params['idModel'] = trelloReviewListID
		response = requests.request("POST", url, headers = headers, params = params)
