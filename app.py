from flask import Flask, render_template, request, redirect, url_for
from neo4j import GraphDatabase, exceptions
from config import NEO4J_USERNAME, NEO4J_PASSWORD

app = Flask(__name__)

# 初始化 Neo4j 数据库连接
uri = "bolt://localhost:7687"
try:
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
except exceptions.ServiceUnavailable as e:
    raise SystemExit("Failed to connect to Neo4j database.") from e

@app.route('/', methods=['GET', 'POST'])
@app.route('/<label>', methods=['GET', 'POST'])
def index(label=None):
    search_query = request.args.get('search', '')  # 获取搜索查询参数

    if request.method == 'POST':
        name = request.form['name']
        label = request.form['label']
        try:
            with driver.session() as session:
                session.run(f"CREATE (p:`{label}` {{name: $name}})", name=name)
        except Exception as e:
            print(f"Error creating node: {e}")

    try:
        with driver.session() as session:
            # 构建基础查询
            if label and label != "AllLabels":
                query = f"MATCH (n:`{label}`) WHERE n.name CONTAINS $search_query RETURN ID(n) AS id, n.name, labels(n)"
            else:
                query = "MATCH (n) WHERE n.name CONTAINS $search_query RETURN ID(n) AS id, n.name, labels(n)"

            node_result = session.run(query, search_query=search_query)
            nodes = [{"id": record["id"], "name": record["n.name"], "labels": record["labels(n)"]} for record in node_result]

            label_result = session.run("CALL db.labels()")
            labels = [record["label"] for record in label_result]
    except Exception as e:
        print(f"Error: {e}")
        nodes, labels = [], []

    return render_template('index.html', nodes=nodes, labels=labels, selected_label=label, search_query=search_query)



@app.route('/show/<int:id>', methods=['GET'])
def show(id):
    """显示特定节点的详细信息。"""
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n, labels(n)", id=id)
            data = result.single()
            if data:
                node = data["n"]
                labels = data["labels(n)"]
            else:
                node, labels = None, []
    except Exception as e:
        print(f"Error retrieving node: {e}")
        node, labels = None, []

    return render_template('show.html', node=node, labels=labels)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    """更新特定节点的信息。"""
    if request.method == 'POST':
        new_name = request.form['new_name']
        try:
            with driver.session() as session:
                session.run("MATCH (n) WHERE ID(n) = $id SET n.name = $new_name", id=id, new_name=new_name)
        except Exception as e:
            print(f"Error updating node: {e}")

        return redirect(url_for('index'))

    # 获取当前节点信息以用于表单预填充
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=id)
            node = result.single()["n"]
    except Exception as e:
        print(f"Error retrieving node for update: {e}")
        node = None

    return render_template('update.html', node=node)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """删除特定节点。"""
    try:
        with driver.session() as session:
            session.run("MATCH (n) WHERE ID(n) = $id DETACH DELETE n", id=id)
    except Exception as e:
        print(f"Error deleting node: {e}")

    return redirect(url_for('index'))

@app.route('/labels', methods=['GET'])
def list_labels():
    """显示数据库中所有唯一的标签。"""
    try:
        with driver.session() as session:
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
    except Exception as e:
        print(f"Error retrieving labels: {e}")
        labels = []

    return render_template('labels.html', labels=labels)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
