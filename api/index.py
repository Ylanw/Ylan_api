# -*- coding: UTF-8 -*-
import requests
import json
from flask import Flask, request, jsonify

def get_github_contributions(username):
    url = f"https://api.github.com/users/{username}/events/public"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MyGitHubApp"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return {"error": "Failed to fetch data from GitHub"}
    
    contributions = {}
    
    for event in data:
        if isinstance(event, dict) and 'created_at' in event:
            date = event['created_at'][:10]
            contributions[date] = contributions.get(date, 0) + 1
    
    sorted_contributions = sorted(contributions.items())
    result = [{"date": date, "count": count} for date, count in sorted_contributions]
    
    return {"total": sum(contributions.values()), "contributions": result}

app = Flask(__name__)

@app.route('/github_contributions', methods=['GET'])
def github_contributions():
    username = request.args.get("user", "").strip()
    if not username or not username.isalnum():
        return jsonify({"error": "Invalid or missing user parameter"}), 400
    
    data = get_github_contributions(username)
    return jsonify(data)

# Vercel 需要 `app` 变量，而不是 `app.run()`
handler = app
