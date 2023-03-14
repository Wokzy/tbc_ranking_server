"""
TurboBattleCity ranking and statistics server

# Note: TLS currently based on self-signed certs
"""


import json
import select
import sqlite3
import threading
import socket as socket_lib

from config import SOCKET_BYTE_LIMIT, ENCODING
from network import Network



class RankingServer(Network):
	def __init__(self):
		"""
		Setting up socket and tls sertificate
		"""

		super().__init__()


	def main(self):
		"""Main loop maintaining connection and processing responces"""

		while self.inputs:
			self.readable, self.writable, self.exceptional = select.select(self.inputs, self.outputs, self.inputs)
			self.process_readable()
			self.process_writable()


	def process_readable(self):
		"""Handle input sockets"""

		for socket in self.readable:
			if socket == self.socket:
				try:
					self.accept_connection()
				except: # This may cause an error when client is asking for tls cert
					continue
			else:
				try:
					data = socket.recv(SOCKET_BYTE_LIMIT).decode(ENCODING)
				except:
					self.disconnect(socket)
					continue

				if not data:
					self.disconnect(socket)
					continue

				threading.Thread(target = self.process_data, args=(socket, data,), daemon=True).start()
				self.outputs.append(socket)


	def process_writable(self):
		"""Handle output sockets"""
		for socket in self.writable:
			if socket in self.responces and not self.responces[socket].empty():
				try:
					data = json.dumps(self.responces[socket].get()).encode(ENCODING)
					socket.send(data)
				except:
					continue


	def process_data(self, socket, data:str):
		"""Recieved data handler"""

		data = json.loads(data) # All requests must have json format!
		self.check_responces_queue(socket)
		self.responces[socket].put(data)

RankingServer().main()
