"""
DB handling script

Server responce statuses

responce - {'status':int, 'content':string}

0 - success
1 - Error
"""


import random
import sqlite3
import hashlib

from config import DATABASE_NAME, USERS_TABLE_NAME, STATS, PASSWORD, PASSWORD_LEN,\
					USERNAME, USERNAME_LEN, PASSWORD_ENCODING



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
			self.cursor.execute(f'CREATE TABLE {USERS_TABLE_NAME} ({USERNAME} varchar({USERNAME_LEN}) NOT NULL, \
								{PASSWORD} varchar({PASSWORD_LEN}) NOT NULL, {STATS} text DEFAULT "{{}}")')
			self.database.commit()


	def check_username_collision(self, username:str):
		"""Checks if username had been already used"""
		return self.cursor.execute(f'SELECT * FROM {USERS_TABLE_NAME} WHERE {USERNAME} = "{username}"').fetchone() != None


	def create_user(self, username:str, password:str):
		"""Makes user-creating request to db by input args"""

		if self.check_username_collision(username = username):
			return {"status":1, "content":'This username already exists, choose smth else'}

		password = create_password_hash(password)
		self.cursor.execute(f'INSERT INTO {USERS_TABLE_NAME} ({USERNAME}, \
							{PASSWORD}) VALUES ("{username}", "{password}")')
		self.database.commit()

		return {"status":0, "content":''}


	def login(self, username:str, password:str):
		"""Matches username and password with database"""
		password = create_password_hash(password)

		user = self.cursor.execute(f'SELECT * FROM {USERS_TABLE_NAME} WHERE {USERNAME} = "{username}"').fetchone()
		if user == None or user[1] != password:
			return {"status":1, "content":'No such login or password'}
		else:
			return {"status":0, "content":'success'}
