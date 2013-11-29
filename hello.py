import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/search/<term>')
def profile(term):
	return "No results for " + term

if __name__ == '__main__':
    app.run(debug=True)
