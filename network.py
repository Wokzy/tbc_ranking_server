"""
Server network parent script
"""

import ssl
import queue
import socket as socket_lib

from config import HOSTING_ADRESS, CERTFILE



class Network:
	def __init__(self):
		"""
		Setting up socket and tls sertificate
		"""

		self.socket = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)
		self.socket.setsockopt(socket_lib.SOL_SOCKET, socket_lib.SO_REUSEADDR, 1)

		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.load_cert_chain(CERTFILE)

		self.socket = context.wrap_socket(self.socket, server_side=True)
		self.socket.bind(HOSTING_ADRESS)
		self.socket.listen()

		self.inputs = [self.socket]
		self.outputs = []

		self.responces = {} # {socket:queue}


	def accept_connection(self):
		"""Handshake and connection acceptance"""

		socket, addr = self.socket.accept()
		socket.setblocking(False)
		self.inputs.append(socket)

		print(f'{addr} is connected') # info print


	def disconnect(self, socket):
		"""Socket disconnection"""

		if socket in self.outputs:
			self.outputs.remove(socket)

		if socket in self.inputs:
			self.inputs.remove(socket)

		if socket in self.responces:
			del self.responces[socket]

		try:
			socket.shutdown(socket_lib.SHUT_RDWR)
		except OSError:
			return
		#socket.close()


	def check_responces_queue(self, socket):
		"""Gets socket and creates queue for it in self.responces"""

		if socket not in self.responces:
			self.responces[socket] = queue.Queue()

