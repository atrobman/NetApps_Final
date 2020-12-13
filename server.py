from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
db_fp = 'data.db' #database filepath

def db_connect():
	'''
	Since we cannot reuse a single connection (since Flask is multithreaded),
	this will create a new connection and cursor for us whenever we need
	'''

	db = sqlite3.connect(db_fp)
	return db, db.cursor()

@app.route('/Login', methods=['POST'])
def login():
	'''
	Return "Success" if the username/password pair is valid login info in the databs
	Return "Failure" otherwise
	'''

	username = request.form['username']
	password = request.form['password']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=? AND Password=?', (username, password))

	if len(cursor.fetchall()) > 0:
		return 'Success'
	
	return 'Failure'

@app.route('/Register', methods=['POST'])
def register():
	'''
	Add a new user to the database. Since usernames are unique identifiers for each user, every
	account must have a different username

	Returns "Success" if the account was registered successfully
	Returns "Failure" if a user with the given username already exists
	'''

	username = request.form['username']
	password = request.form['password']
	name = request.form['name']
	email = request.form['email']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

	if len(cursor.fetchall()) > 0:
		return 'Failure'
		
	cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (username, password, name, email))
	db.commit()
	return 'Success'

@app.route('/Delete', methods=['POST'])
def delete_user():
	'''
	Delete a user from the database. As an extra measure of security, a valid username/password pair is required

	Returns "Success" if the account was deleted successfully
	Returns "Failure" if invalid username/password pair is provided
	'''

	username = request.form['username']
	password = request.form['password']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=? AND Password=?', (username, password))

	if len(cursor.fetchall()) < 1:
		return 'Failure'

	cursor.execute('DELETE FROM users WHERE Username=?', (username,))
	cursor.execute('DELETE FROM results WHERE Username=?', (username,))
	db.commit()
	return 'Success'

@app.route('/Results', methods=['POST'])
def get_user_results():
	'''
	Request all of a user's past survey scores

	Returns a json with the following fields:
		"Scores": a list of total scores for past surveys
		"Timestamps": a parallel list to scores that holds a datetime timestamp for each survey
	'''

	username = request.form['username']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM results WHERE Username=?', (username,))
	res = cursor.fetchall()
	msg = {
		'Scores': [x[1] for x in res],
		'Timestamps': [datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f').strftime("%m/%d/%Y") for x in res]
	}

	return msg

@app.route('/Add_Result', methods=['POST'])
def add_user_result():
	'''
	Add a new survey result to the database

	Returns "Success" if the score was added successfully
	Returns "Failure" if the provided username could not be found in the database
	'''

	username = request.form['username']
	score = request.form['score']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

	if len(cursor.fetchall()) < 1:
		return 'Failure'

	cursor.execute('INSERT INTO results VALUES (?, ?, ?)', (username, score, datetime.now()))
	db.commit()
	return 'Success'

@app.route('/User_Info', methods=['POST'])
def get_user_info():
	'''
	Request a user's account info

	Returns a json with the following fields:
		"Username": The account's username
		"Password": The account's password
		"Name": The name of the account's user
		"Email": The attached email account to the user's account
	'''

	username = request.form['username']
	password = request.form['password']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=? AND Password=?', (username, password))

	res = cursor.fetchall()
	msg = dict()

	if len(res) < 1:
		return msg
	
	res = res[0]

	msg['Username'] = res[0]
	msg['Password'] = res[1]
	msg['Name'] = res[2]
	msg['Email'] = res[3]

	return msg

if __name__ == '__main__':

	#On startup, check if the database file exists
	create_table = False
	if (db_fp not in os.listdir('.')):
		create_table = True

	db, cursor = db_connect()

	#If the database file did not already exist, we need to create the tables in the database
	if (create_table):
		cursor.execute('CREATE TABLE users (Username text, Password text, Name text, Email text)')
		cursor.execute('CREATE TABLE results (Username text, Score int, Timestamp DATETIME)')
		db.commit()
	
	app.run(host='0.0.0.0', port=5001, debug=True)