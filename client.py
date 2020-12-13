from flask import Flask, render_template, request, make_response
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import os
import time

app = Flask(__name__)

#function used to plot all of the results for a given user. 
#takes in a variable s which is the result of a request.post to the backend
#to get the user's results
#The function returns the name of the file to be displayeed 
def plotResults(s):
    #default name for plot if the current user has no scores
    new_graph_name = "default_image.png"
    #if we get a bad status_code or the length of scores is equal to 0 we return the default image name
    if(s.status_code == 200):
        if(len(s.json()['Scores']) > 0):
            #plots scores as a blue line with dots on each point
            plt.plot(s.json()['Scores'], 'b-o', label="Scores")
            plt.ylabel("Stress Score")
            #plots a threshold horizantal line for being stressed out
            maxI = len(s.json()['Timestamps'])
            plt.hlines(15, 0, max(maxI-1, 1), 'r', label="Stress Threshold")
            #gets average score of all scores for the current user and plots it on the graph as a horizontal line
            avgOfScores = sum([int(x) for x in s.json()['Scores']])/len(s.json()['Scores'])
            plt.hlines(avgOfScores, 0, max(maxI-1, 1), 'g', label="Average Score")
            #limits our y range to possible survey scores
            plt.ylim(0, 25)
            #rotates the x labels to make them more readable
            plt.xticks(rotation=30)
            plt.title("Results Graph")
            #allows multiple results from the same date to display correctly
            plt.xticks(np.arange(len(s.json()['Timestamps'])), s.json()['Timestamps'])
            #shows a legend for all lines on plot
            plt.legend()
            #makes the plot fit the screen well
            plt.tight_layout()
            #due to websites remebering previous images we have to save this plot with a unique filename (which we did with the time library
            new_graph_name = "results" + str(time.time()).replace('.', '-') + ".png"
            #we then go through our images directiory and delete any other result images that may still be there
            for filename in os.listdir('static/'):
                if filename.startswith('results'):  # not to remove other images
                    os.remove('static/' + filename)
            #now we can save our new plot and close the plot
            plt.savefig('static/' + new_graph_name)
            plt.close()
    return new_graph_name

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        #whenever we get to the login page we want to clear user cookies
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
                #get results from backend
                s = requests.post(f"http://localhost:5001/Results", data={"username":request.form["Username"]})
                #plot the results
                new_graph_name = plotResults(s)
                resp = make_response(render_template("homepage.html", results=new_graph_name))
                #if we logged in successfully we set the cookies
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


#prompts user for login info to confirm account deletion
@app.route('/Delete', methods=['POST', 'GET'])
def deleteAccount():
    if request.method == 'GET':
        return render_template("deleteAccount.html")

#checks users login info to see if we should actually delete the account or send them back to the home page
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
            #if a user successfully registers we send them to the homepage
            if r.text == "Success":
                s = requests.post(f"http://localhost:5001/Results", data={"username":request.form["registerUsername"]})
                new_graph_name = plotResults(s)
                resp = make_response(render_template("homepage.html", results=new_graph_name))
                resp.set_cookie('username', request.form["registerUsername"])
                resp.set_cookie('password', request.form["registerPassword"])
                return resp
            #else we send them to the login screen
            else:
                return render_template("login.html")


@app.route('/Results', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        #calculates the sum of all the user input from the backend
        sumOfScores = sum([int(x) for x in request.form.values()])
        #we add the result to the database using the post statement
        r = requests.post(f"http://localhost:5001/Add_Result", data={"username":request.cookies.get('username'), "score":sumOfScores})
        if r.status_code == 200:
            if r.text == "Success":
                #now we get user_info so we can pass the provided email into the html file in the line below
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
