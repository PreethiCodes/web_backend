from flask import Flask, request, redirect, jsonify, Blueprint
from pymongo import MongoClient
from datetime import datetime
from user_agents import parse
import json
import requests
from collections import Counter
import os
from dotenv import load_dotenv
from modules.db import db

collection = db["urls"]


class AnalyticsModule:
    def __init__(self):
        self.bp = Blueprint("analytics", __name__, url_prefix="/analytics")
        self.register_routes()

    def register_routes(self):
        @self.bp.route("/<short>")
        def get_info_and_redirect(short):
            # location from ip address
            def get_location(ip):
                url = f"http://ip-api.com/json/{ip}"
                try:
                    response = requests.get(url, timeout=5)  # Add a timeout
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    data = response.json()
                    return {
                        "country": data.get("country", "Unknown"),
                        "region": data.get("regionName", "Unknown"),
                        "city": data.get("city", "Unknown"),
                    }
                except requests.exceptions.RequestException as e:
                    return {
                        "country": "Unknown",
                        "region": "Unknown",
                        "city": "Unknown",
                    }

            url = collection.find_one({"shortCode": short})
            if not url:
                return "URL not found", 404

            # getting impression whenever unfurled
            UNFURL_BOTS = [
                "facebookexternalhit",
                "Twitterbot",
                "Slackbot-LinkExpanding",
                "Discordbot",
                "WhatsApp",
                "LinkedInBot",
            ]
            user_agent = request.headers.get("User-Agent", "")
            if any(bot in user_agent for bot in UNFURL_BOTS):
                result = collection.update_one(
                    {"shortCode": short}, {"$inc": {"impressions": 1}}, upsert=False
                )

                # Return simple HTML response
                return f"""
                <html>
                <head>
                    <title>{short} is unfurled</title>
                </head>
                <body>
                    <h1>shortcode for this url: </h1>
                </body>
                </html>
                """

            # Getting the data of a click
            now = datetime.utcnow()
            iso = now.isoformat()
            user_agent = parse(request.user_agent.string)
            if request.headers.get("X-Forwarded-For"):
                ip_address = request.headers.get("X-Forwarded-For").split(",")[
                    0
                ]  # first ip in the list
            else:
                ip_address = request.remote_addr

            location_data = get_location(ip_address)
            click_data = {
                "date_time": iso,
                "day": now.strftime("%A"),
                "device": user_agent.device.family,
                "os": user_agent.os.family,
                "browser": user_agent.browser.family,
                "ip": ip_address,
                "country": location_data["country"],
                "region": location_data["region"],
                "city": location_data["city"],
            }
            # unique visitors
            collection.update_one(
                {"shortCode": short},
                [
                    {
                        "$set": {
                            "unique_visitors_list": {
                                "$cond": {
                                    "if": {
                                        "$in": [ip_address, "$unique_visitors_list"]
                                    },
                                    "then": "$unique_visitors_list",  # No change
                                    "else": {
                                        "$concatArrays": [
                                            "$unique_visitors_list",
                                            [ip_address],
                                        ]
                                    },  # Add new IP
                                }
                            },
                            "unique_visitors": {
                                "$cond": {
                                    "if": {
                                        "$in": [ip_address, "$unique_visitors_list"]
                                    },
                                    "then": "$unique_visitors",  # No increment
                                    "else": {
                                        "$add": ["$unique_visitors", 1]
                                    },  # Increment
                                }
                            },
                        }
                    }
                ],
            )

            # adding click data
            collection.update_one(
                {"shortCode": short}, {"$push": {"click_data": click_data}}
            )

            # incrementing clicks
            collection.update_one({"shortCode": short}, {"$inc": {"clicks": 1}})

            return redirect(url["longUrl"])

        # Displaying ctr
        @self.bp.route("/ctr/<short>")
        def getctr(short):
            url = collection.find_one({"shortCode": short})
            if not url:
                return "short code not found"
            if "click_data" not in url:
                return "No clicks yet"
            if "impressions" not in url:
                return "No impressions yet"
            clicks = len(url.get("click_data"))
            impressions = url.get("impressions")
            ctr = round(clicks / (clicks + impressions), 2)
            display = {
                "shortCode": short,
                "ctr": ctr,
                "totalImpressions": clicks + impressions,
                "clicks": clicks,
            }
            return jsonify(display)

        # Displaying analytics
        @self.bp.route("/analytics/<short>")
        def get_analytics(short):
            # * this is fine for now, but we might end up changing this soon
            url = collection.find_one({"shortCode": short})
            if not url:
                return "Short code does not exist", 404
            clicks = url["clicks"]

            device = Counter(click["device"] for click in url["click_data"])
            os = Counter(click["os"] for click in url["click_data"])
            browser = Counter(click["browser"] for click in url["click_data"])

            display = {
                "shortCode": short,
                "totalClicks": clicks,
                "uniqueVisitors": url.get("unique_visitors", 0),
                "deviceDistribution": device,
                "osDistribution": os,
                "browserDistribution": browser,
            }
            return jsonify(display)

        @self.bp.route("/recent")
        def recent():
            # Find the most recently created record using _id
            url = collection.find_one(
                sort=[("_id", -1)]
            )  # Sort by _id in descending order

            if not url:
                return jsonify({"error": "No records found"}), 404

            # Format the response
            recent_url = {
                "shortCode": url["shortCode"],
                "longUrl": url["longUrl"],
                "createdAt": url["createdAt"],
                "expiryDate": url["expiryDate"],
                "clicks": url["clicks"],
                "base64img": url["base64img"],
            }

            return jsonify(recent_url), 200

        @self.bp.route("/all")
        def all():
            urls = collection.find()
            all_urls = []
            for url in urls:
                all_urls.append(
                    {
                        "shortCode": url.get("shortCode", ""),
                        "longUrl": url.get("longUrl", ""),
                        "createdAt": url.get("createdAt", ""),
                        "expiryDate": url.get("expiryDate", ""),
                        "clicks": url.get("clicks", 0),
                    }
                )
            return jsonify(all_urls), 200

    def get_blueprint(self):
        return self.bp
