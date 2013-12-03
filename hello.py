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
	return render_template('searchform.html')

@app.route('/search/<term>')
def profile(term):
	db = load_db()
	q = """select ?r where { ?d <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.uniprot.org/core/Protein>
        . ?d <http://purl.uniprot.org/core/mnemonic> ?r}"""
	db.query(q)
	r = db.query(q)
	return render_template('searchresults.html', results=(rr[0] for rr in r))

if __name__ == '__main__':
    app.run(debug=True)


