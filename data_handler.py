"""
Script for handling recieved_data

Server responce statuses

responce - {'status':int, 'content':string}

0 - success
1 - Error
"""

import json
import database

#from config import USERNAME, PASSWORD


class Handler:
	def __init__(self):
		"""Initting database and etc"""
		self.database = database.DataBase()


	def handle(self, request:str):
		"""Head handling function"""

		try:
			request = json.loads(request)
		except json.decoder.JSONDecodeError:
			return {"status":1, "content":"Something wrong with request"}

		try:
			match request['request']:
				case 'create_user':
					return self.database.create_user(username = request['username'], password = request['password'])
				case 'login':
					return self.database.login(username = request['username'], password = request['password'])
				case 'get_user_stats':
					return self.database.get_user_stats(username = request['username'])
				case 'apply_changes':
					return self.database.apply_changes(username = request['username'], password = request['password'],
														changes = request['changes'])
		except ValueError:
			return {'status':1, 'content':"Incorrect request"}

