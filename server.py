from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)
db_fp = 'data.db'

def db_connect():
	db = sqlite3.connect(db_fp)
	return db, db.cursor()

@app.route('/Register', methods=['POST'])
def register():
	username = request.form['username']
	password = request.form['password']
	name = request.form['name']
	email = request.form['email']

	db, cursor = db_connect()

	cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

	if len(cursor.fetchall()) > 0:
		return 'False'
	
	cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (username, password, name, email))
	db.commit()
	return 'True'

@app.route('/View')
def view():
	db, cursor = db_connect()
	cursor.execute('SELECT * FROM users')
	return str(cursor.fetchall())

if __name__ == '__main__':

	create_table = False
	if (db_fp not in os.listdir('.')):
		create_table = True

	db, cursor = db_connect()

	if (create_table):
		cursor.execute('CREATE TABLE users (Username text, Password text, Name text, Email text)')
		db.commit()
	
	app.run(host='0.0.0.0', port=5000, debug=True)