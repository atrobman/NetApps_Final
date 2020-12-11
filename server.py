from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
db_fp = 'data.db'

def db_connect():
	db = sqlite3.connect(db_fp)
	return db, db.cursor()

@app.route('/Login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=? AND Password=?', (username, password))

	if len(cursor.fetchall()) > 0:
		return 'Success'
	
	return 'Failure'

@app.route('/Register', methods=['POST'])
def register():
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

	username = request.form['username']

	db, cursor = db_connect()

	cursor.execute('SELECT Score FROM results WHERE Username=?', (username,))

	msg = {
		'Scores': cursor.fetchall()
	}

	return msg

@app.route('/Add_Result', methods=['POST'])
def add_user_result():

	username = request.form['username']
	score = request.form['score']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

	if len(cursor.fetchall()) < 1:
		return 'Failure'

	cursor.execute('INSERT INTO results VALUES (?, ?)', (username, score))
	db.commit()
	return 'Success'

if __name__ == '__main__':

	create_table = False
	if (db_fp not in os.listdir('.')):
		create_table = True

	db, cursor = db_connect()

	if (create_table):
		cursor.execute('CREATE TABLE users (Username text, Password text, Name text, Email text)')
		cursor.execute('CREATE TABLE results (Username text, Score int)')
		db.commit()
	
	app.run(host='0.0.0.0', port=5000, debug=True)