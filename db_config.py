from configurations import configurations

config = configurations.get_config()

username = config["pythonAnywhereUsername"]
password = config["pythonAnywherePassword"]
hostname = f"{username}.mysql.pythonanywhere-services.com"
databasename = config["pythonAnywhereDatabaseName"]

SQLALCHEMY_DATABASE_URI = (f"mysql://{username}:{password}@{hostname}/{username}${databasename}")
SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 299}
SQLALCHEMY_TRACK_MODIFICATIONS = False
