from concurrent.futures import ThreadPoolExecutor
import requests
import json
import time

urls = """random urls"""
urls = urls.split('\n')

def MassRequest(url):
    a = time.perf_counter()
    req = requests.post("http://127.0.0.1:8000/scrape",json={"url":url})
    print(req.json()['blocked'])
    print(req.status_code)
    b = time.perf_counter()
    print(f'{round(b-a)} seconds.')

with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(MassRequest,urls)
    