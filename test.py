import requests

url = 'https://pypi.python.org/packages/source/D/Django/Django-1.7.tar.gz#md5=03edab6828119aa9b32b2252d25eb38d'

response = requests.get(url, stream=True)
f = open('django.tar.gz', 'wb')
for i, chunk in enumerate(response.raw.stream(4096)):
    f.write(chunk)
    print i, len(chunk)
f.close()
