import requests
import os
from flask import Flask, render_template, request, send_from_directory
import json

base_url = "http://hn.algolia.com/api/v1"

# This URL gets the newest stories.
new = f"{base_url}/search_by_date?tags=story"

# This URL gets the most popular stories
popular = f"{base_url}/search?tags=story"


# This function makes the URL to get the detail of a storie by id.
# Heres the documentation: https://hn.algolia.com/api
def make_detail_url(id):
  return f"{base_url}/items/{id}"


def get_news(mode):
  response = requests.get(mode).text
  response = json.loads(response)
  
  news = []
  for res in response['hits']:
    mydict = {}
    mydict['title'] = res['title']
    mydict['id'] = res['objectID']
    mydict['url'] = res['url']
    mydict['points'] = res['points']
    mydict['author'] = res['author']
    mydict['comments'] = res['num_comments']
    news.append(mydict)
  return news    


def get_detail(id):
  url = make_detail_url(id)
  response = requests.get(url).text
  response = json.loads(response)

  news_info = {}
  news_info['title'] = response['title']
  news_info['points'] = response['points']
  news_info['author'] = response['author']
  news_info['url'] = response['url']
  news_info['children'] = response['children']

  return news_info


db = {}
app = Flask("DayNine")

@app.route("/")
def home():
  NEW = "new"
  POP = "popular"
  mode = request.args.get('order_by') # 쿼리 받아오기
  if mode:
    mode = mode.lower()
  else: # 기본모드시 popular mode 로 set
    mode = POP
  
  if mode == POP:
    if db.get(POP):
      news = db[POP]
    else:
      news = get_news(popular)
      db[POP] = news
  else:
    if db.get(NEW):
      news = db[NEW]
    else:
      news = get_news(new)
      db[NEW] = news

  return render_template('index.html', length=len(news), mode=mode, news=news) # html파일 렌더 및 변수 넘겨주기

@app.route("/<id>")
def news_detail(id):
  news_info = get_detail(id)
  return render_template('detail.html',
  news=news_info,
  length=len(news_info['children']),
  comments=news_info['children'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


app.run(host="0.0.0.0")