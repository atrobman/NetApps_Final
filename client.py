from flask import Flask, render_template, request, make_response
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
import time

# IMAGE_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)

# app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        resp = make_response(render_template("login.html"))
        resp.set_cookie('username', "", expires=0)
        resp.set_cookie('password', "", expires=0)
        return resp
    


@app.route('/homePage', methods=['POST', 'GET'])
def homePage():
    if request.method == 'POST':
        r = requests.post(f"http://localhost:5001/Login", data={"username":request.form["Username"], "password":request.form["Password"]})
        if r.status_code == 200:
            if r.text == "Success":
                s = requests.post(f"http://localhost:5001/Results", data={"username":request.form["Username"]})
                if(s.status_code == 200):
                    plt.plot(s.json()['Timestamps'], s.json()['Scores'], 'b-o')
                    plt.ylabel("Stress Score")
                    new_graph_name = "results" + str(time.time()).replace('.', '-') + ".png"
                    for filename in os.listdir('static/'):
                        if filename.startswith('results'):  # not to remove other images
                            os.remove('static/' + filename)
                    plt.savefig('static/' + new_graph_name)
                    plt.close()
                resp = make_response(render_template("homepage.html", results=new_graph_name))
                resp.set_cookie('username', request.form["Username"])
                resp.set_cookie('password', request.form["Password"])
                return resp
            else:
                return render_template("login.html")
    else:
        _username = request.cookies.get('username')
        s = requests.post(f"http://localhost:5001/Results", data={"username":_username})
        if(s.status_code == 200):
            plt.plot(s.json()['Scores'], 'b-o')
            plt.ylabel("Stress Score")
            new_graph_name = "results" + str(time.time()).replace('.', '-') + ".png"
            for filename in os.listdir('static/'):
                if filename.startswith('results'):  # not to remove other images
                    os.remove('static/' + filename)
            plt.savefig('static/' + new_graph_name)
            plt.close()
            return render_template("homepage.html", results=new_graph_name)
        else:
            return render_template("homepage.html", results="default.png")
      

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
                resp = make_response(render_template("homepage.html"))
                resp.set_cookie('username', request.form["registerUsername"])
                resp.set_cookie('password', request.form["registerPassword"])
                return resp
            else:
                return render_template("login.html")


@app.route('/Results', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        result = request.form
        sumOfScores = sum([int(x) for x in request.form.values()])
        r = requests.post(f"http://localhost:5001/Add_Result", data={"username":request.cookies.get('username'), "score":sumOfScores})
        if r.status_code == 200:
            if r.text == "Success":
                resp = make_response(render_template("result.html", result=result))
                return resp
            else:
                resp = make_response(render_template("login.html"))
                resp.set_cookie('username', "", expires=0)
                resp.set_cookie('password', "", expires=0)
                return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
