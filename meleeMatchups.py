from flask import *
from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired
from bs4 import BeautifulSoup
from apiclient.discovery import build

import requests
import sys
import time
import json

DEVELOPER_KEY = 'AIzaSyCztDnA9Jq7RxtujCWuE37YhOE1kOz6FXA'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

yt = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEY)
app = Flask(__name__)
app.config.from_object('config')
videos = list()
ytVideos = list()
vidTitles = list()

characters = [('', ''), ('Mario', 'Mario'), ('Luigi', 'Luigi'), 
('Yoshi','Yoshi'), ('DonkeyKong', 'Donkey Kong'), ('Link','Link'), 
('Samus','Samus'), ('Kirby','Kirby'), ('Fox','Fox'), ('Pikachu', 'Pikachu'), 
('Jigglypuff', 'Jigglypuff'), ('CaptainFalcon','Captain Falcon'), ('Ness','Ness') 
,('Peach','Peach'), ('Bowser','Bowser'), ('DrMario','Dr.Mario'), ('Zelda','Zelda'), 
('Sheik','Sheik'), ('Ganondorf','Ganondorf'), ('YoungLink', 'Young Link'), 
('Falco','Falco'), ('Mewtwo','Mewtwo') , ('Pichu','Pichu'), ('IceClimbers' ,'Ice Climbers'), 
('Marth', 'Marth'), ('Roy','Roy'), ('GameAndWatch', 'Game & Watch')]

date1 = "01/01/2014"
date2 = time.strftime("%m/%d/%y")

 # Take a BeautifulSoup object and pull all the youtube links from it 
def addVids(soup):
	for link in soup.find_all('a'):
		vid = link.get('href')
		if vid and vid.find('youtube') != -1:
			videos.append(vid)

#uses the youtube API to get  video information for each ytId that was pulled			
def parseVids():
	ytIds = [video[video.find('=') + 1:] for video in videos]
	ytVideos = [yt.videos().list(part = 'snippet, statistics, id', id = vidId).execute() for vidId in ytIds]

	for vid in ytVideos:
		if not vid or not vid['items'] :
			ytVideos.remove(vid)
	ytVideos.sort(key = lambda x: int(x['items'][0]['statistics']['viewCount']), reverse = True)

	vidTitles = [vid['items'][0]['snippet']['title'] for vid in ytVideos]
	return ["https://www.youtube.com/watch?v=" + vid['items'][0]['id'] for vid in ytVideos], vidTitles

#makes requests to smashVods while there are still pages left with youtube links. Then parses these vids
#and sets the form's links to the proper amount of videos
def getVideos(form):
	videos[:] = []
	char1 = form.char1.data
	char2 = form.char2.data
	if not char1:
		char1 = 'All'
	if not char2: 
		char2 = 'All'
	player1 = form.player1.data
	player2 = form.player2.data
	params = {'char1':char1, 'player1' : player1, 'char2': char2, 'player2':player2, 'date1': date1, 'date2':date2, 'page' : 1}
	count = 1
	while True:
		allInfo = requests.get('http://smashvods.com/ssbm', params = params)
		soup = BeautifulSoup(allInfo.text, 'html.parser')
		if any ((link.get('href').find('youtube') != -1) for link in soup.find_all('a')): 
			addVids(soup)
			count += 1
			params['page'] = count
		else: break
	(form.vidLinks,form.titles) = parseVids()
	form.vidLinks = form.vidLinks[:form.numVids.data]
#our form
class infoForm(Form):
	char1 = SelectField('Character 1:', choices = characters)
	char2 = SelectField('Character 2:', choices = characters)
	player1 = StringField('Player 1:')
	player2 = StringField('Player 2:')
	numVids = IntegerField('How many videos to display?', default = 10)
	vidLinks = list()
	titles = list()

#some basic routing
@app.route("/")
@app.route("/index" ,methods = ['GET', 'POST'])
def index():
	
	form = infoForm()
	if request.method == 'POST':
		getVideos(form)

	return render_template('index.html', form = form)

if __name__ == "__main__":
	characters.sort()
	app.run(debug = True)