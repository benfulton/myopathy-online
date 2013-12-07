import os
import rdflib
from flask import Flask, render_template

app = Flask(__name__)
db = None
pref = """PREFIX prot:   <http://purl.uniprot.org/core/>
          PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
          PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX cite:   <http://purl.uniprot.org/citations/>
"""

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
    r = db.query(q)
    for foo in r:
        print foo
    return render_template('proteins.html', results=r)

@app.route('/protein/<mnemonic>')
def protein(mnemonic):
    db = load_db()
    q = """select ?fn ?d where { ?d rdf:type prot:Protein; prot:mnemonic "%s"; prot:recommendedName ?n .
           ?n prot:fullName ?fn }"""
    print pref + q % mnemonic
    r = db.query( pref + q % mnemonic)
    print "Result count",len(r)
    return render_template('protein.html', results=r, mnemonic=mnemonic)

@app.route('/articles')
def articles():
    db = rdflib.Graph()
    db.parse("articles.rdf", format="xml")
    q = """select ?r ?d where { ?d <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.uniprot.org/core/Journal_Citation>
        . ?d <http://purl.uniprot.org/core/title> ?r}"""
    r = db.query(q)
    return render_template('articles.html', results=r)

@app.route('/article/<pmid>')
def article(pmid):
    db = rdflib.Graph()
    db.parse("articles.rdf", format="xml")
    q = """select ?d ?author ?comment where
            { cite:%s rdf:type
              prot:Journal_Citation;
              prot:title ?d;
              prot:author ?author;
              rdfs:comment ?comment }"""
    print pref + q % pmid
    r = db.query(pref + q % pmid)
    d = dict(title = list(r)[0][0], authors = [f[1] for f in r], pmid=pmid, comment=list(r)[0][2])
    return render_template('article.html', article= d)

@app.route('/search')
def search():
    return render_template('searchform.html')

if __name__ == '__main__':
    app.run(debug=True)


