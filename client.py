from flask import Flask, render_template, request, make_response
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import os
import time

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        resp = make_response(render_template("login.html"))
        resp.set_cookie('username', "", expires=0)
        resp.set_cookie('password', "", expires=0)
        return resp
    
def plotResults(s):
    new_graph_name = "default_image.png"
    if(s.status_code == 200):
        if(len(s.json()['Scores']) > 0):
            avgOfScores = sum([int(x) for x in s.json()['Scores']])/len(s.json()['Scores'])
            plt.plot(s.json()['Scores'], 'b-o', label="Scores")
            plt.ylabel("Stress Score")
            maxI = len(s.json()['Timestamps'])
            plt.hlines(15, 0, max(maxI-1, 1), 'r', label="Stress Threshold")
            plt.hlines(avgOfScores, 0, max(maxI-1, 1), 'g', label="Average Score")
            plt.ylim(0, 25)
            plt.xticks(rotation=30)
            plt.title("Results Graph")
            plt.xticks(np.arange(len(s.json()['Timestamps'])), s.json()['Timestamps'])
            plt.legend()
            new_graph_name = "results" + str(time.time()).replace('.', '-') + ".png"
            for filename in os.listdir('static/'):
                if filename.startswith('results'):  # not to remove other images
                    os.remove('static/' + filename)
            plt.tight_layout()
            plt.savefig('static/' + new_graph_name)
            plt.close()
    return new_graph_name

@app.route('/homePage', methods=['POST', 'GET'])
def homePage():
    if request.method == 'POST':
        r = requests.post(f"http://localhost:5001/Login", data={"username":request.form["Username"], "password":request.form["Password"]})
        if r.status_code == 200:
            if r.text == "Success":
                s = requests.post(f"http://localhost:5001/Results", data={"username":request.form["Username"]})
                new_graph_name = plotResults(s)
                resp = make_response(render_template("homepage.html", results=new_graph_name))
                resp.set_cookie('username', request.form["Username"])
                resp.set_cookie('password', request.form["Password"])
                return resp
            else:
                return render_template("login.html")
    else:
        _username = request.cookies.get('username')
        s = requests.post(f"http://localhost:5001/Results", data={"username":_username})
        new_graph_name = plotResults(s)
        return render_template("homepage.html", results=new_graph_name)
      

@app.route('/survey', methods=['POST', 'GET'])
def survey():
    if request.method == 'GET':
        return render_template("survey.html")


@app.route('/Delete', methods=['POST', 'GET'])
def deleteAccount():
    if request.method == 'GET':
        return render_template("deleteAccount.html")


@app.route('/deleteAccount', methods=['POST', 'GET'])
def deleteAccountActually():
    if request.method == 'POST':
        _username = request.cookies.get('username')
        _password = request.cookies.get('password')
        if _username == request.form["deleteUsername"] and _password == request.form["deletePassword"]:
            r = requests.post(f"http://localhost:5001/Delete", data={"username":_username, "password":_password})
            if r.status_code == 200:
                if r.text == "Success":
                    resp = make_response(render_template("login.html"))
                    resp.set_cookie('username', "", expires=0)
                    resp.set_cookie('password', "", expires=0)
                    return resp
                else:
                    return render_template("homepage.html")
        else:
            return render_template("homepage.html")

@app.route('/Register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        r = requests.post(f"http://localhost:5001/Register", data={"username":request.form["registerUsername"], "password":request.form["registerPassword"], "email":request.form["email"], "name":request.form["fullName"]})
        if r.status_code == 200:
            if r.text == "Success":
                s = requests.post(f"http://localhost:5001/Results", data={"username":request.form["registerUsername"]})
                new_graph_name = plotResults(s)
                resp = make_response(render_template("homepage.html", results=new_graph_name))
                resp.set_cookie('username', request.form["registerUsername"])
                resp.set_cookie('password', request.form["registerPassword"])
                return resp
            else:
                return render_template("login.html")


@app.route('/Results', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        sumOfScores = sum([int(x) for x in request.form.values()])
        r = requests.post(f"http://localhost:5001/Add_Result", data={"username":request.cookies.get('username'), "score":sumOfScores})
        if r.status_code == 200:
            if r.text == "Success":
                s = requests.post("http://localhost:5001/User_Info", data={"username":request.cookies.get('username'), "password":request.cookies.get('password')})
                resp = make_response(render_template("result.html", result=sumOfScores, email=s.json()['Email']))
                return resp
            else:
                resp = make_response(render_template("login.html"))
                resp.set_cookie('username', "", expires=0)
                resp.set_cookie('password', "", expires=0)
                return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
