"""
Script for handling recieved_data

Server responce statuses

responce - {'status':int, 'content':string}

0 - success
1 - Error
"""

import json
import database

from config import GAME_SERVER_SIGNATURE, AVERAGE_MMR_CHANGE, MATCHES_STATS_LIMIT,\
					MIN_MMR



def dict_quick_sort(lst:list, key):
	"""Quick sort implementation for list with dicts"""

	if len(lst) < 2:
		return lst

	bigger = []
	equal = [lst[0]]
	less = []

	for i in range(1, len(lst)):
		if lst[i][key] < lst[0][key]:
			less.append(lst[i])
		elif lst[i][key] == lst[0][key]:
			equal.append(lst[i])
		else:
			bigger.append(lst[i])

	return dict_quick_sort(bigger, key) + equal + dict_quick_sort(less, key)


class Handler:
	"""Requests handler"""
	def __init__(self):
		"""Initting database and etc"""
		self.database = database.DataBase()


	def handle(self, request:str):
		"""Head handling function"""

		try:
			request = json.loads(request)
		except json.decoder.JSONDecodeError:
			return {"status":1, "content":"Something wrong with request"}

		responce = None
		try:
			match request['request']:
				case 'create_user':
					responce = self.database.create_user(username = request['username'],
														password = request['password'])
				case 'login':
					responce = self.database.login(username = request['username'],
													password = request['password'])
				case 'get_user_stats':
					responce = self.database.get_user_stats(username = request['username'])
				case 'account_changes':
					responce = self.database.account_changes(username = request['username'],
								password = request['password'], changes = request['changes'])
				case 'get_all_users':
					responce = {'status':0, 'content':self.database.get_all_users()}
				case 'get_top_players':
					responce = self.get_top_players()
				case 'count_rankings':
					responce = self.count_rankings(users=request['users'], signature=request['signature'])
		except ValueError:
			responce = {'status':1, 'content':"Incorrect request"}

		return responce


	def get_top_players(self, amount:int = 10):
		"""Returns top {amount} players"""

		users = dict_quick_sort([{'username':data[0], 'MMR':json.loads(data[2])['MMR']} for data in self.database.get_all_users()], key = 'MMR')[:amount:]
		string = f'rank|  {"username":^12}  |  MMR\n' + '-'*27 + '\n'

		for i in range(len(users)):
			string += f"{i + 1:<2}  |  {users[i]['username']:^12}  |  {users[i]['MMR']}\n"

		return {'status':0, 'content':string}



	def count_rankings(self, users:list, signature:str):
		"""Count MMR and stats after finished game on server*"""

		if signature != GAME_SERVER_SIGNATURE:
			return {'status':1, 'content':'Incorrect signature'}

		users = dict_quick_sort(users, 'score')
		mmr_below = 0
		mmr_above = 0

		for i  in range(len(users)):
			users[i]['stats'] = self.database.get_user_stats(username = users[i]['username'])
			if users[i]['stats']['status']:
				return {'status':1, 'content':f'User error {users[i]["username"]}'}

			users[i]['stats'] = users[i]['stats']['content']
			mmr_below += users[i]['stats']['MMR']


		for i in range(len(users)):
			change = 0
			mmr_below -= users[i]['stats']['MMR']
			if i > 0:
				avg_above = mmr_above // i
				change -= int(min(AVERAGE_MMR_CHANGE * (1 / (avg_above / users[i]['stats']['MMR'])) * (1 + .2*i), 
									users[i]['stats']['MMR'] - MIN_MMR))

			if i < len(users) - 1:
				avg_below = mmr_below // (len(users) - i - 1)
				change += int(AVERAGE_MMR_CHANGE * (avg_below / users[i]['stats']['MMR']) * (1 + .2*i))

			mmr_above += users[i]['stats']['MMR']
			users[i]['stats']['MMR'] += change

			if 'matches' not in users[i]['stats']:
				users[i]['stats']['matches'] = []

			users[i]['stats']['matches'].insert(0, change)
			users[i]['stats']['matches'] = users[i]['stats']['matches'][:10:]

			self.database.stats_changes(username = users[i]['username'], signature=signature, stats=users[i]['stats'])
