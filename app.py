import requests
resp = requests.get('https://www.instagram.com/', proxies={'http': "http://156.239.35.57:4444:b8b6743778:k5UGVbPr"}, timeout=4)
print(resp.status_code)