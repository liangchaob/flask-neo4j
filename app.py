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
        label = request.form['label']
        with driver.session() as session:
            session.run(f"CREATE (p:{label} {{name: $name}})", name=name)
    
    # 省略其他代码...
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN ID(n) AS id, n.name, labels(n)")
        nodes = [{"id": record["id"], "name": record["n.name"], "labels": record["labels(n)"]} for record in result]

    return render_template('index.html', nodes=nodes)

@app.route('/show/<int:id>', methods=['GET'])
def show(id):
    with driver.session() as session:
        result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n, labels(n)", id=id)
        data = result.single()
        if data:
            node = data["n"]
            labels = data["labels(n)"]
        else:
            node, labels = None, []

    return render_template('show.html', node=node, labels=labels)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        new_name = request.form['new_name']
        with driver.session() as session:
            session.run("MATCH (n) WHERE ID(n) = $id SET n.name = $new_name", id=id, new_name=new_name)
        # 其余代码不变...

        return redirect(url_for('index'))

    # 获取当前节点信息以用于表单预填充
    with driver.session() as session:
        result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=id)
        node = result.single()["n"]

    return render_template('update.html', node=node)


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    with driver.session() as session:
        session.run("MATCH (n) WHERE ID(n) = $id DETACH DELETE n", id=id)
        
    return redirect(url_for('index'))


@app.route('/labels', methods=['GET'])
def list_labels():
    with driver.session() as session:
        result = session.run("CALL db.labels()")
        labels = [record["label"] for record in result]
    return render_template('labels.html', labels=labels)





if __name__ == '__main__':
    app.run(debug=True,port=5001)
