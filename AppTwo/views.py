from django.shortcuts import render
from django.http import HttpResponse
from flask import Flask, abort, request
from uuid import uuid4
from .models import Article
import datetime
import requests
import requests.auth
import urllib
import random
# Create your views here.

articleCount = 20

def nytimes(request):
    d = {'key' : nytimesList()}
    return render(request, 'nytimes.html', d)
    #return HttpResponse(r)

def nytimesList():
    time_period = '1'   # day = 1, week = 7, month = 30
    api_key = '7279eea0382343b18de9593c8d0c8148'
    r = requests.get('https://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/'+time_period+'.json?api-key='+ api_key)
    json_object = r.json()

    articleList = []
    for i in range(articleCount):
        a = {
            'title' : json_object['results'][i]['title'],
            'abstract' : json_object['results'][i]['abstract'],
            'url' : json_object['results'][i]['url'],
            'pub_date' : json_object['results'][i]['published_date'],
            'source' : 'NYTimes'
        }
        articleList.append(a)

    # Save 1st article in database
    agregarDB(articleList[0])

    return articleList


#!/usr/bin/env python
CLIENT_ID = "7U69qIihV3RDIQ"
CLIENT_SECRET = "R5AbYpT1fXIus7JLLcGkpFt97cc"
REDIRECT_URI = "http://127.0.0.1:8000/reddit/"


def user_agent():
    '''reddit API clients should each have their own, unique user-agent
    Ideally, with contact info included.

    e.g.,
    return "oauth2-sample-app by /u/%s" % your_reddit_username
    '''
    raise NotImplementedError()

def base_headers():
    return {"User-Agent": user_agent()}


app = Flask(__name__)
@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with reddit</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True

@app.route('/reddit_callback')
def reddit_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    access_token = get_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    return "Your reddit username is: %s" % get_username(access_token)

def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)
    token_json = response.json()
    return token_json["access_token"]


def get_username(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    return me_json['name']


if __name__ == '__main__':
    app.run(debug=True, port=65010)


def reddit(request):
    d = {'key' : redditList()}
    return render(request, 'reddit.html', d)
    #return HttpResponse(r)

def redditList():
    clientID = '7U69qIihV3RDIQ'
    secret = 'R5AbYpT1fXIus7JLLcGkpFt97cc'
    username = 'noeldelgadom'
    uri = 'http://127.0.0.1:8000/reddit/'
    r = requests.get(r'http://www.reddit.com/hot.json')
    json_object = r.json()

    articleList = []
    for i in range(articleCount):
        date = datetime.datetime.fromtimestamp(json_object['data']['children'][i]['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S')
        a = {
            'title' : json_object['data']['children'][i]['data']['title'],
            'url' : json_object['data']['children'][i]['data']['url'],
            'pub_date' : date[:10],
            'source' : 'Reddit',
        }
        articleList.append(a)

    # Save 1st article in database
    agregarDB(articleList[0])

    return articleList

def index(request):
    articleList = nytimesList() + redditList()
    random.shuffle(articleList)
    d = {'key' : articleList}
    return render(request, 'index.html', d)

def agregarDB(d):
    new_article = Article()
    new_article.title = d['title']
    new_article.url = d['url']
    new_article.pub_date = d['pub_date']
    new_article.source = d['source']
    new_article.save()
