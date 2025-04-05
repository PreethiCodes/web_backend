from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from datetime import datetime
from user_agents import parse
import json
import requests
app=Flask(__name__)
from flask import Blueprint

app_sub = Blueprint('app_sub',__name__, url_prefix='/sub')


client=MongoClient('mongodb://localhost:27017/')
db=client['shortly']
collection=db['urls']

@app_sub.route('/<short>')
def get_info_and_redirect(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "URL not found",404
    #Getting the data of a click
    now=datetime.utcnow()
    user_agent=parse(request.user_agent.string)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    url=f"http://ip-api.com/json/{ip_address}"
    response=requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
    else:
        return {"error": "Failed to get geolocation"}
    click_data = {
        "time": now.strftime("%H:%M:%S"),
        "date": now.day,
        "month": now.strftime("%B"),
        "year": now.year,
        "day": now.strftime("%A"),
        "device": user_agent.device.family,
        "os": user_agent.os.family,
        "browser": user_agent.browser.family,
        "ip": ip_address,
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country_name"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "org": data.get("org")}
    
    #Getting unique visitors
   
    #Updating MongoDB
    
    

    collection.update_one(
        {"shortCode": short},
        {"$push": {"click_data": click_data}}
    )
    #originalurl
    ourl=collection.find_one({"shortCode":short})

    
    return redirect(ourl['longUrl'])

#Getting impressions for ctr
@app_sub.route('/impression/<short>')
def count_impression(short):
    collection.update_one(
        {"shortCode": short},
        {"$inc": {"impressions": 1}}, 
        upsert=True 
    )
    return "Impression counted", 200

#Diplaying ctr
@app_sub.route('/ctr/<short>')
def getctr(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "short code not found"
    if "clicks" not in url:
        return "No clicks yet"
    if "impressions" not in url:
        return "No impressions yet"
    clicks=len(url['clicks'])
    impressions=url['impressions']
    ctr=clicks/impressions
    display={"shortCode": short, "ctr": ctr, "totalImpressions": impressions, "clicks": clicks}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

#Displaying analytics
@app_sub.route('/analytics/<short>')
def get_analytics(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "Short code does not exist", 404
    clicks=len(url['clicks'])
    device={}
    os={}
    browser={}
    for click in url['clicks']:
        if click['device'] not in device:
            device[click['device']]=1
        else:
            device[click['device']]+=1
        if click['os'] not in os:
            os[click['os']]=1
        else:
            os[click['os']]+=1
        if click['browser'] not in browser:
            browser[click['browser']]=1
        else:
            browser[click['browser']]+=1

    display={"shortCode": short, "totalClicks": clicks, "uniqueVisitors": url.get('unique_visitors',0), "deviceDistribution": device, "osDistribution": os, "browserDistribution": browser}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

if __name__=='__main__':
    app.run(debug=True)
