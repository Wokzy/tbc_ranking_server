'''
Constants and configuration file for server
'''

import json

HOSTING_ADDRESS = ('0.0.0.0', 42113) # (IP, PORT)
SOCKET_BYTE_LIMIT = 1024 # send/recv

CERTFILE = 'certificate.pem' # Name of TLS certfile to be loaded (MUST BE SELF-SIGNED!)

ENCODING = 'utf-8'

GAME_SERVER_SIGNATURE = '' # Enter signature sync string for sessions servers

DATABASE_NAME = 'stats.db'

MIN_MMR = 100
AVERAGE_MMR_CHANGE = 30

USERS_TABLE_NAME = 'Users'
USERNAME = 'nickname'
USERNAME_LEN = 12
STATS = 'stats'
PASSWORD = 'password'
PASSWORD_LEN = 64 # sha256 hash
PASSWORD_ENCODING = 'utf-32'
CREATION_DATE = 'creation_date'
DEFAULT_STATS = json.dumps({'MMR':MIN_MMR, 'ProCircuit':0, "matches":[]})
MATCHES_STATS_LIMIT = 10


# Match stat structure {"date":, "players":, "place":, "MMR":}



"""
Request structure
{'request':..., "{content}":.., "{content}":....}

possible requests:
	create user

Server responce statuses

responce - {'status':int, 'content':string}

0 - success
1 - Error
"""

