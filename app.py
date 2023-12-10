from flask import Flask, render_template, request, redirect, url_for
from neo4j import GraphDatabase
from config import NEO4J_USERNAME, NEO4J_PASSWORD

# Neo4j 数据库连接
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) # 使用你的用户名和密码


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        with driver.session() as session:
            session.run("CREATE (p:Person {name: $name})", name=name)
    
    with driver.session() as session:
        result = session.run("MATCH (p:Person) RETURN p.name")
        names = [record["p.name"] for record in result]

    return render_template('index.html', names=names)

@app.route('/details/<name>', methods=['GET'])
def details(name):
    return render_template('details.html', name=name)

@app.route('/update/<name>', methods=['GET', 'POST'])
def update(name):
    if request.method == 'POST':
        new_name = request.form['new_name']
        with driver.session() as session:
            session.run("MATCH (p:Person {name: $name}) SET p.name = $new_name", name=name, new_name=new_name)
        return redirect(url_for('index'))
    
    return render_template('update.html', name=name)

@app.route('/delete/<name>', methods=['POST'])
def delete(name):
    with driver.session() as session:
        session.run("MATCH (p:Person {name: $name}) DELETE p", name=name)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,port=5001)
