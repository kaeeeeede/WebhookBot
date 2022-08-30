from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("db_config")
db = SQLAlchemy(app)
ENDPOINT_MAX_LENGTH = 25

@app.route("/")
def main():
    return "200"

@app.route("/githubPullRequest", methods = ["POST"])
def fetchDetails():
	endpoint = "/githubPullRequest"
	payload = request.json

	new_task = Job(endpoint = endpoint, payload = payload)
	db.session.add(new_task)
	db.session.commit()

	return payload

@app.route("/trelloMovedToBoard", methods = ["HEAD"])
def init_webhook():
    print("Webhook initialized.")

    return "200"

@app.route("/trelloMovedToBoard", methods = ["POST"])
def movedToBoard():
	endpoint = "/trelloMovedToBoard"
	payload = request.json

	new_task = Job(endpoint = endpoint, payload = payload)
	db.session.add(new_task)
	db.session.commit()

	return payload

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    endpoint = db.Column(db.String(ENDPOINT_MAX_LENGTH), nullable = False)
    payload = db.Column(db.JSON)

if __name__ == "__main__":
    db.create_all()
