#!/usr/bin/env python3

import socket

class Client:
	def __init__(self, host, port):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((host, port))

			#Get username
			self.username = s.recv(1024).decode()
			if self.username == 'CREATE':
				self.username = input("Server: Please create a username: ")
				s.sendall(self.username.encode())

			while True:
				#Send user data
				client_data = input(f"{self.username}: ")
				if not client_data:
					break
				s.sendall(client_data.encode())


if __name__ == '__main__':
	c = Client('127.0.0.1', 5000)