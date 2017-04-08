import csv

def check_credentials(username, password):
	"""
	:return True if credentials exists in database
	"""
	with open('users.csv', 'rb') as file:
		reader = csv.reader(file, delimiter=',')
		for row in reader:
			if row[0] == username and row[1] == password:
				return True
	return False

def check_username(username):
	"""
	:return True if username exists in database
			False else
	"""
	with open('users.csv', 'rb') as file:
		reader = csv.reader(file, delimiter=',')
		for row in reader:
			if row[0] == username:
				return True
	return False

def new_user(username, password):
	"""
	:return True if username is new and details are written to file
	"""
	if check_username(username):
		return False
	with open('users.csv', 'a') as file:
		writer = csv.writer(file, delimiter=',')
		writer.writerow([username, password])
		return True
	return False


























