from flask import Flask, request, jsonify, redirect, render_template, session, url_for
from algoliasearch.search_client import SearchClient

# Auth0: Import
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv


# Flask
app = Flask(__name__)


# Algolia
client = SearchClient.create('SF0IKHXEOM', '68ff5251ad7e59a3da88bd09b7994d53')
index = client.init_index('test_arXiv')


# Auth0
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app.secret_key = env.get("APP_SECRET_KEY")
oauth = OAuth(app)


oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Home: Route for home page, Auth0: Controllers API, without Auth0, only an index.html will be rendered here.
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template(
        "index.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


# Algolia: Route for handling search requests
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')

    if query:
        response = index.search(query)  # Perform the Algolia search
        hits = response['hits']  # Extract relevant data from the search response
        return jsonify(hits)  # Return the search results as JSON
    else:
        return jsonify([])


# Algolia: Route for handling detail page
@app.route('/detail/<object_id>', methods=['GET'])
def detail(object_id):
    paper = index.get_object(object_id)  # Retrieve the paper data from Algolia based on the objectID

    if paper:
        return render_template('detail.html', paper=paper)
    else:
        return "Paper not found", 404  # Handle the case where the paper is not found


# Auth0: Call back
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


# Auth0: Login
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


# Auth0: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
    # without Auth0, here is "app.run(debug=True)", and the app is running on localhost:5000/
