from django.test import Client
from django.test.utils import setup_test_environment
setup_test_environment()
c=Client()
r=c.get('/venue/212a79cc-42bc-44ad-ac8b-4364cadc35bd/')
html=r.content.decode('utf-8')
print('STATUS', r.status_code)
print('HAS INIT STRING:', 'Initializing venue detail with data' in html)
print('HAS JSON.parse:', 'JSON.parse' in html)
start = html.find('id="map-link"')
if start!=-1:
    snippet=html[start:start+200]
    print('MAP SNIPPET:', snippet)
else:
    print('MAP LINK NOT FOUND')
