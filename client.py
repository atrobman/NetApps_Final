from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/survey', methods=['POST', 'GET'])
def survey():
    if request.method == 'POST':
        return render_template("survey.html")


@app.route('/result', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        result = request.form
        return render_template("result.html", result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
