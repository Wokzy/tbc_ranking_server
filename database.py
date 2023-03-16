"""
DB handling script

Server responce statuses

responce - {'status':int, 'content':string}

0 - success
1 - Error
"""


import time
import json
import random
import sqlite3
import hashlib

from config import DATABASE_NAME, USERS_TABLE_NAME, STATS, PASSWORD, PASSWORD_LEN,\
					USERNAME, USERNAME_LEN, PASSWORD_ENCODING, DEFAULT_STATS, CREATION_DATE



def create_password_hash(password:str):
	return hashlib.sha256(password.encode(PASSWORD_ENCODING)).hexdigest()


class DataBase:
	def __init__(self):
		self.database = sqlite3.connect(DATABASE_NAME)
		self.cursor = self.database.cursor()

		self.check_tables_creation()


	def check_tables_creation(self):
		"""Tryes to select smth from crucial tables and creates them, wether error"""

		try:
			self.cursor.execute(f'SELECT * FROM {USERS_TABLE_NAME};')
		except sqlite3.OperationalError:
			self.cursor.execute(f"CREATE TABLE {USERS_TABLE_NAME} ({USERNAME} varchar({USERNAME_LEN}) NOT NULL, \
								{PASSWORD} varchar({PASSWORD_LEN}) NOT NULL, {STATS} text DEFAULT '{DEFAULT_STATS}',\
								{CREATION_DATE} text NOT NULL)")
			self.database.commit()


	def create_user(self, username:str, password:str):
		"""Makes user-creating request to db by input args"""

		if self.get_user(username) != None:
			return {"status":1, "content":'This username already exists, choose smth else'}

		password = create_password_hash(password)
		self.cursor.execute(f'INSERT INTO {USERS_TABLE_NAME} ({USERNAME}, \
							{PASSWORD}, {CREATION_DATE}) VALUES ("{username}", "{password}", "{time.asctime()}")')
		self.database.commit()

		return {"status":0, "content":''}


	def get_user(self, username:str):
		"""Returns user's string from database"""
		return self.cursor.execute(f'SELECT * FROM {USERS_TABLE_NAME} WHERE {USERNAME} = "{username}"').fetchone()


	def login(self, username:str, password:str):
		"""Matches username and password with database"""
		password = create_password_hash(password)

		user = self.get_user(username)
		if user == None or user[1] != password:
			return {"status":1, "content":'No such username or password'}
		else:
			return {"status":0, "content":'login success'}


	def get_user_stats(self, username:str):
		"""Return user's stats dict"""

		user = self.get_user(username)
		if user == None:
			return {"status":1, "content":'This user does not exist'}

		return {"status":0, "content":json.loads(user[2])}


	def apply_changes(self, username:str, password:str, changes:dict):
		"""Recieves user changes and applies it wether everything is correct"""
		# Changes struct: {'nickname':current username, 'password':, 'stats':dict}

		login = self.login(username, password)
		if login['status'] == 1:
			return login

		if 'username' not in changes:
			changes['username'] = username
		if 'password' not in changes:
			changes['password'] = password

		changes['password'] = create_password_hash(changes['password'])

		user = self.get_user(username)
		if (changes['username'], changes['password'], changes['stats']) != user:
			if type(changes['stats']) == dict:
				changes['stats'] = json.dumps(changes['stats'])

			self.cursor.execute(f'UPDATE {USERS_TABLE_NAME} SET {USERNAME} = "{changes["username"]}",\
											{PASSWORD} = "{changes["password"]}", {STATS} = \'{changes["stats"]}\' WHERE {USERNAME} = "{username}"')
			self.database.commit()

		return {"status":0, "content":"Changes applied"}

