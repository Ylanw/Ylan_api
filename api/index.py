# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json
import logging
from functools import lru_cache

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    'Referer': 'https://github.com/',
    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    'X-Requested-With': 'XMLHttpRequest'
}

DATE_REGEX = re.compile(r'data-date="(.*?)" id="contribution-day-component')
COUNT_REGEX = re.compile(r'<tool-tip .*?class="sr-only position-absolute">(.*?) contribution')

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

@lru_cache(maxsize=32)
def getdata(name):
    headers = HEADERS.copy()
    headers['Referer'] += name
    
    try:
        gitpage = requests.get(f"https://github.com/{name}?action=show&controller=profiles&tab=contributions&user_id={name}", headers=headers)
        gitpage.raise_for_status()
        data = gitpage.text
    except requests.RequestException as e:
        logging.error(f"Error fetching data from GitHub: {e}")
        return {"total": 0, "contributions": []}

    datadate = DATE_REGEX.findall(data)
    datacount = COUNT_REGEX.findall(data)
    datacount = list(map(int, [0 if i == "No" else i for i in datacount]))

    if not datadate or not datacount:
        logging.warning("No data found for user.")
        return {"total": 0, "contributions": []}

    sorted_data = sorted(zip(datadate, datacount))
    datadate, datacount = zip(*sorted_data)

    contributions = sum(datacount)
    datalist = [{"date": item, "count": datacount[index]} for index, item in enumerate(datadate)]
    datalistsplit = list_split(datalist, 7)
    
    returndata = {
        "total": contributions,
        "contributions": datalistsplit
    }
    
    return returndata

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if '?' in path:
            user = path.split('?')[1]
        else:
            user = ''
        
        if not user:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "User not specified"}).encode('utf-8'))
            return
        
        data = getdata(user)
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        return
