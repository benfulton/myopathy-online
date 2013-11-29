import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
	return render_template('searchform.html')

@app.route('/search/<term>')
def profile(term):
	return render_template('searchresults.html', results=[term])

if __name__ == '__main__':
    app.run(debug=True)
