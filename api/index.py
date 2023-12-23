# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    try:
        gitpage = requests.get("https://github.com/" + name)
        gitpage.raise_for_status()  # 检查请求是否成功
        data = gitpage.text

        datadatereg = re.compile(r'data-date="(.*?)" data-level')
        datacountreg = re.compile(r'<span class="sr-only">(.*?) contribution')

        datadate = datadatereg.findall(data)
        datacount = datacountreg.findall(data)
        
        # 添加异常处理，确保数据转换成功
        datacount = list(map(lambda x: 0 if x == "No" else int(x), datacount))

        # 将datadate和datacount按照字典序排序
        sorted_data = sorted(zip(datadate, datacount))
        datadate, datacount = zip(*sorted_data)

        contributions = sum(datacount)

        datalist = []
        for index, item in enumerate(datadate):
            itemlist = {"date": item, "count": datacount[index]}
            datalist.append(itemlist)

        datalistsplit = list_split(datalist, 7)

        returndata = {
            "total": contributions,
            "contributions": datalistsplit
        }
        return returndata

    except Exception as e:
        # 在发生异常时记录错误信息
        print(f"Error in getdata: {e}")
        return {"error": "Failed to fetch data"}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            user = path.split('?')[1]

            # 添加对用户输入的合法性检查，防止非法输入导致错误
            if not user:
                raise ValueError("Invalid user parameter")

            data = getdata(user)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            # 在发生异常时记录错误信息
            print(f"Error in do_GET: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal Server Error"}).encode('utf-8'))
