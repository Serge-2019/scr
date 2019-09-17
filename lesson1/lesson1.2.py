import requests
from pprint import pprint
import json

head = {'User-agent': 'Mozilla/5.0'}
endpoint = 'http://httpbin.org/basic-auth/user/pass'

req = requests.get(endpoint, headers=head, auth=('user', 'pass'))

if req.ok:
    data = json.loads(req.text)
    pprint(data)
else:
    print('ERROR')
