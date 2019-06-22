#!/usr/bin/env python3

import socket
import json
import ntplib
import os
from time import ctime

#Create the NTP client to handle login times
ntp_client = ntplib.NTPClient()
def get_time():
	try:
		req = ntp_client.request('pool.ntp.org')
		return ctime(req.tx_time)
	except Exception as e:
		print("Server: Time error, could not connect to NTP server ", e)
		return "T_ERROR"

class Server:
	def __init__(self, host, port):
		if os.path.isfile('database.json') == False:
			print("Server: No user database file found creating..")
			with open('database.json', 'w') as file:
				json.dump({}, file)

		with open('database.json', 'r') as file:
			self.database = json.loads(file.read())

		#Connection starts here
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
			server_socket.bind((host, port))
			server_socket.listen()
			print("Server: Running, waiting for connections..")
			conn, addr = server_socket.accept()

			#Handle incoming/outgoing data and connections
			try:
				with conn:
					username = self.get_username(addr[0], conn)
					self.handle_login(addr[0], username, get_time())

					while True:
						data = conn.recv(1024).decode()
						if not data:
							break

						self.log_message(addr[0], data)
						print(f"{username}: {data}")

				self.handle_logout(addr[0], username, get_time())

			#Handle forced disconnects
			except Exception as e:
				try:
					self.handle_logout(addr[0], username, get_time())
				except Exception as f:
					#User never made it pass creating username ignore
					pass

	def get_username(self, ip, conn):
		user_data = self.database.get(ip)
		#New user
		if user_data == None:
			conn.sendall(b'CREATE')
			username = conn.recv(1024).decode()
		
			self.database[ip] = {
				"username" : username,
				"login_history" : [],
				"logout_history" : [],
				"chat_history" : []
			}
		else:
			username = self.database[ip]['username']
			conn.sendall(username.encode())

		return username

	def handle_login(self, ip, username, _time):
		#Logs and announces the login time
		self.database[ip]['login_history'].append(_time)
		print(f"Server: {username} has connected to the server on " + _time)

	def handle_logout(self, ip, username, _time):
		self.database[ip]['logout_history'].append(_time)
		print(f"Server: {username} has left the server on " + _time)

		with open('database.json', 'w') as file:
			json.dump(self.database, file, indent=4)

	def log_message(self, ip, msg):
		self.database[ip]["chat_history"].append(msg)


if __name__ == '__main__':
	s = Server('127.0.0.1', 5000)