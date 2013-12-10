import os
import rdflib
from flask import Flask, render_template, Response

app = Flask(__name__)
db = None
article_db = None
pref = """PREFIX prot:   <http://purl.uniprot.org/core/>
          PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
          PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX myo:   <http://myopathy-online.herokuapp.com/ontology/>
"""

def load_db():
    global db
    if db == None:
        db = rdflib.Graph()
        db.parse("myopathy.rdf", format="xml")
    return db

def load_articles():
    global article_db
    if article_db == None:
        article_db = rdflib.Graph()
        article_db.parse("articles.rdf", format="xml")
    return article_db

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

@app.route('/articles/page/<page>')
def articles(page):
    db = load_articles()
    q = """select ?title ?cite where
            { ?cite rdf:type myo:article;
              myo:title ?title }
           order by ?title
           limit 20
           offset %s
            """
    print pref + q
    r = db.query(pref + q % ((int(page)-1) * 20))
    return render_template('articles.html', results=r, page=int(page))

@app.route('/articles/author/<author>')
def articles_by_author(author):
    db = load_articles()
    q = """select ?title ?cite where
            { ?cite rdf:type myo:article;
              myo:title ?title;
              myo:author "%s" }
           order by ?title
            """
    print pref + q
    r = db.query(pref + q % author)
    return render_template('articles.html', results=r, page=1, author=author)

@app.route('/articles/journal/<journal>')
def articles_by_journal(journal):
    db = load_articles()
    q = """select ?title ?cite where
            { ?cite rdf:type myo:article;
              myo:title ?title;
              myo:journal "%s" }
           order by ?title
            """
    print pref + q
    r = db.query(pref + q % journal)
    return render_template('articles.html', results=r, page=1, author=journal)

@app.route('/article/<pmid>')
def article(pmid):
    db = load_articles()
    q = """select ?title ?author ?abstract ?journal where
            { <http://myopathy-online.herokuapp.com/ontology/article/%s> rdf:type myo:article;
              myo:title ?title;
              myo:author ?author;
              myo:journal ?journal;
              myo:abstract ?abstract }"""
    r = db.query(pref + q % pmid)
    d = dict(title=list(r)[0][0], authors=[f[1] for f in r], pmid=pmid, comment=list(r)[0][2], journal=list(r)[0][3])
    return render_template('article.html', article= d)

@app.route('/ontology')
def ontology():
    with open("myopathy1.2.owl") as f:
        return Response(f.read(), mimetype='application/rdf+xml')

@app.route('/search')
def search():
    return render_template('searchform.html')

if __name__ == '__main__':
    app.run(debug=True)


