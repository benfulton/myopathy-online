import os
import rdflib
from flask import Flask, render_template, Request, Response

app = Flask(__name__)
ontology = None
article_db = None
pref = """PREFIX prot:   <http://purl.uniprot.org/core/>
          PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
          PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX myo:   <http://myopathy-online.herokuapp.com/ontology/>
"""
pref2 = """PREFIX prot:   <http://purl.uniprot.org/core/>
      PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
      PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
      PREFIX cite:   <http://purl.uniprot.org/citations/>
      PREFIX myo:    <http://myopathy-online.herokuapp.com/ontology#>"""

def load_articles():
    global article_db
    if article_db == None:
        article_db = rdflib.Graph()
        article_db.parse("articles.rdf", format="xml")
    return article_db

def load_ontology():
    global ontology
    if ontology == None:
        ontology = rdflib.Graph()
        ontology.parse("onto.owl", format="n3")
    return ontology

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/proteins')
def proteins():
    q = """select ?x  where { ?x a myo:proteins } order by ?x"""
    r = load_ontology().query(pref2 + q)
    return render_template('proteins.html', results=r)

@app.route('/protein/<mnemonic>')
def protein(mnemonic):
    q = """select ?x ?y where { myo:%s ?x ?y }"""
    r = load_ontology().query(pref2 + q % mnemonic)
    for x in r:
        print x
    return render_template('protein.html', results=r, mnemonic=mnemonic)

@app.route('/articles/page/<page>')
def articles(page):
    q = """select ?title ?cite where
            { ?cite rdf:type myo:article;
              myo:title ?title }
           order by ?title
           limit 20
           offset %s
            """
    r = load_articles().query(pref + q % ((int(page)-1) * 20))
    return render_template('articles.html', results=r, page=int(page))

@app.route('/articles/author/<author>')
def articles_by_author(author):
    q = """select ?title ?cite where
            { ?cite rdf:type myo:article;
              myo:title ?title;
              myo:author "%s" }
           order by ?title
            """
    r = load_articles().query(pref + q % author)
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
def get_ontology():
    with open("myopathy1.2.owl") as f:
        return Response(f.read(), mimetype='application/rdf+xml')

@app.route('/sparql', methods=['POST'])
def sparql_results():
    db = load_articles()
    q = Request.form['query']
    db.query(q)
    return render_template('sparql.html')


@app.route('/diseases')
def diseases():
    q = """select ?y  where { { ?x rdfs:subClassOf myo:inherited } union { ?x rdfs:subClassOf myo:acquired }.
                                ?y a ?x } order by ?y"""
    r = load_ontology().query(pref2 + q)
    return render_template('diseases.html', results=r)

@app.route('/disease/<mnemonic>')
def disease(mnemonic):
    q = """select ?x ?y where { myo:%s ?x ?y }"""

    print pref + q % mnemonic
    r = load_ontology().query( pref + q % mnemonic)
    print "Result count",len(r)
    return render_template('disease.html', results=r, mnemonic=mnemonic)

@app.route('/gene/<mnemonic>')
def gene(mnemonic):
    q = """select ?y ?type ?rel where { myo:%s ?rel ?y. ?y a ?type }"""

    print pref2 + q % mnemonic
    r = load_ontology().query( pref + q % mnemonic)
    print "Result count",len(r)
    return render_template('gene.html', results=r, mnemonic=mnemonic)

@app.route('/sparql')
def sparql():
    return render_template('sparql.html')

@app.route('/search')
def search():
    return render_template('searchform.html')

if __name__ == '__main__':
    app.run(debug=True)


