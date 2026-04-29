"""This module provides a very simple client to interact with an ASGI app using HTTP. The class is meant
to allow reusing test cases based on fir.wsgi.Client."""
import asyncio
from fir import http
from fir.wsgi import request_to_environ
from typing import Awaitable


def request_to_scope(request: http.Request, server_name: str = "") -> dict:
	"""Converts a HTTP request into a ASGI scope dictionary.

	Args:
		request: a HTTP request.

	Returns:
		A scope dictionary.
	"""
	return {
		"type": "http",
		"http_version": "1.1",
		"method": request.method,
		"path": request.path,
		"query_string": request.query,
		"headers": [(k.encode(), v.encode()) for k, v in request.headers.items()]
	}


class ASGIClient:

	__slots__ = ("_app", )

	def __init__(self, app: Awaitable):
		self._app = app

	def request(self, req: http.Request) -> http.Response:
		return asyncio.run(self.async_request(req))

	async def async_request(self, req: http.Request) -> http.Response:
		call = _ASGIHTTPCall(req)
		await self._app(call.scope, call.receive, call.send)
		return call.get_response()


class _ASGIHTTPCall:

	__slots__ = ("scope", "_body", "_receive_flag", "_status", "_headers", "_output")

	def __init__(self, request: http.Request):
		self.scope = request_to_scope(request)
		self._body = request.get_body()
		self._receive_flag = True
		self._output = b''

	async def receive(self) -> dict:
		if self._receive_flag:
			self._receive_flag = False
			return {
				"type": "http.request",
				"body": self._body,
				"more_body": False
			}
		else:
			while True:
				await asyncio.sleep(1)

	async def send(self, message: dict):
		if message["type"] == "http.response.start":
			self._status = message['status']
			self._headers = message['headers']
		elif message["type"] == "http.response.body":
			self._output += message['body']
		else:
			raise ValueError(f"Unsupported message {message}")

	def get_response(self)-> http.Response:
		return http.Response(
			status_code=self._status,
			status_message=http.STATUS_MESSAGES.get(self._status, ""),
			headers={k.decode(): v.decode() for k, v in self._headers},
			body=self._output
		)
