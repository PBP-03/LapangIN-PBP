import re
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','lapangin.settings')
import django
django.setup()
from django.test import Client
c=Client()
r=c.get('/lapangan/')
s=r.content.decode('utf-8')
hrefs=re.findall(r'href=[\"\'](/venue/[^\"\']+)[\"\']', s)
print('\n'.join(hrefs[:10]))
