import os
import rdflib
from flask import Flask, render_template

app = Flask(__name__)
db = None

def load_db():
	global db
	if db == None:
		db = rdflib.Graph()
		db.parse("myopathy.rdf", format="xml")
	return db

@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/proteins')
def proteins():
	db = load_db()
	q = """select ?r ?d where { ?d <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.uniprot.org/core/Protein>
        . ?d <http://purl.uniprot.org/core/mnemonic> ?r}"""
	db.query(q)
	r = db.query(q)
	return render_template('proteins.html', results=r)

@app.route('/articles')
def articles():
	db = rdflib.Graph()
	db.parse("articles.rdf", format="xml")
	q = """select ?r ?d where { ?d <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.uniprot.org/core/Journal_Citation>
        . ?d <http://purl.uniprot.org/core/title> ?r}"""
	db.query(q)
	r = db.query(q)
	return render_template('articles.html', results=r)

@app.route('/search')
def search():
	return render_template('searchform.html')

if __name__ == '__main__':
    app.run(debug=True)


