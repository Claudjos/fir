# About
Provides utilities to convert WSGI environ/output to HTTP Request/Response. The main use case for this package is WSGI APP testing through its WSGI client.

## Install
```
pip install pyfir
```

## How to test your WSGI APP

#### Basic example
test_api.py
```
from fir.wsgi import Client
from fir.http import Request
from <package.module> import app # for example your Flask APP


# Create a WSGI Client
client = Client(app)


def test_api():
	# Use the client to perform request to your APP
	res = client.request(Request(
		method="GET",
		uri="/customers"
	))
	assert res.status_code == 200
	assert res.get_json() == [{"name":"john", "surname": "doe"}]

```

#### Example of data driven tests
test_api.py
```
import unittest
from ddt import ddt, file_data
from fir.wsgi import Client
from fir.http import Request
from <package.module> import app # for example your Flask APP


# Create a WSGI Client
client = Client(app)


@ddt
class WSGITestCase(unittest.TestCase):

	@file_data('data.yaml')
	def test_api(self, request, response):
		global client
		res = client.request(Request(**request))
		assert res.status_code == response.get("status")
		if res.headers.get("content-type") == "application/json":
			assert res.get_json() == response.get("json")

```
data.yaml
```
- request:
	method: GET
	uri: /customers
  response:
	status: 200
	json:
	- name: jhon
	  surname: doe

- request:
	method: GET
	uri: /customers/mark
  response:
	status: 404
```

## Unit test
```
pip install -r test-requirements.txt
python -m pytest tests/ --cov=fir
```