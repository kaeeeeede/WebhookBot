import trello
from configurations import configurations

config = configurations.get_config()
trelloManager = trello.trelloManager(config)
trelloManager.initWebhook(config["trelloReviewListID"], config["hostURL"])