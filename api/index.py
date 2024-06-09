# File: index.py

import re
import requests
import json
from time import sleep
from http.server import BaseHTTPRequestHandler

def list_split(items, n):
    """Split list into chunks of size n"""
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(base_url, name):
    """Fetch and process GitHub user contribution data"""
    headers = {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        # Send the request
        gitpage = requests.get(f"{base_url}?{name}", headers=headers)
        gitpage.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        return {"error": str(e)}

    data = gitpage.text
    datadatereg = re.compile(r'data-date="(.*?)" id="contribution-day-component')
    datacountreg = re.compile(r'<tool-tip .*?class="sr-only position-absolute">(.*?) contribution')

    datadate = datadatereg.findall(data)
    datacount = datacountreg.findall(data)
    datacount = list(map(lambda x: 0 if x == "No" else int(x), datacount))

    if not datadate or not datacount:
        return {"total": 0, "contributions": []}

    sorted_data = sorted(zip(datadate, datacount))
    datadate, datacount = zip(*sorted_data)

    contributions = sum(datacount)
    datalist = [{"date": item, "count": datacount[index]} for index, item in enumerate(datadate)]
    datalistsplit = list_split(datalist, 7)

    return {
        "total": contributions,
        "contributions": datalistsplit
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        base_url = "http://example.com/api"
        user = path.split('?')[-1]
        
        if not user:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing user parameter')
            return

        data = getdata(base_url, user)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

# File: test_index.py

import unittest
from index import list_split, getdata, handler
from unittest.mock import patch, MagicMock
import json

class TestListSplit(unittest.TestCase):
    def test_list_split(self):
        self.assertEqual(list_split([1, 2, 3, 4], 2), [[1, 2], [3, 4]])
        self.assertEqual(list_split([1, 2, 3], 2), [[1, 2], [3]])
        self.assertEqual(list_split([], 2), [])

class TestGetData(unittest.TestCase):
    @patch('index.requests.get')
    def test_getdata_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<div data-date="2023-01-01" id="contribution-day-component"></div>' \
                             '<tool-tip class="sr-only position-absolute">5 contributions</tool-tip>'
        mock_get.return_value = mock_response

        data = getdata('http://example.com/api', 'valid_user')
        self.assertIn('total', data)
        self.assertIn('contributions', data)

    @patch('index.requests.get')
    def test_getdata_no_contributions(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<div></div>'
        mock_get.return_value = mock_response

        data = getdata('http://example.com/api', 'no_contributions')
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['contributions'], [])

    @patch('index.requests.get')
    def test_getdata_error(self, mock_get):
        mock_get.side_effect = requests.RequestException('Error')
        data = getdata('http://example.com/api', 'invalid_user')
        self.assertIn('error', data)

class TestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = handler

    @patch('index.getdata')
    def test_do_GET(self, mock_getdata):
        mock_getdata.return_value = {"total": 5, "contributions": []}

        request = MagicMock()
        request.path = '/?testuser'
        self.handler.do_GET(request)

        request.send_response.assert_called_with(200)
        request.send_header.assert_called_with('Content-type', 'application/json')
        request.end_headers.assert_called()
        request.wfile.write.assert_called_with(json.dumps({"total": 5, "contributions": []}).encode('utf-8'))

if __name__ == '__main__':
    unittest.main()
