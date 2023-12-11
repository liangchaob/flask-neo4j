from flask import Flask, render_template, request, redirect, url_for, jsonify
from neo4j import GraphDatabase, exceptions
from config import NEO4J_USERNAME, NEO4J_PASSWORD
from datetime import datetime
from neo4j.time import DateTime

app = Flask(__name__)

# 初始化 Neo4j 数据库连接
uri = "bolt://localhost:7687"
try:
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
except exceptions.ServiceUnavailable as e:
    raise SystemExit("Failed to connect to Neo4j database.") from e

@app.route('/', methods=['GET', 'POST'])
@app.route('/filter/<selected_label>', methods=['GET'])
def index(selected_label=None):
    """处理首页的请求，显示所有节点或根据标签过滤节点。"""
    search_query = request.args.get('search', '')  # 获取搜索查询参数

    # 处理创建节点的请求
    if request.method == 'POST':
        label = request.form['label']
        properties = {'name': request.form['name']}
        # 处理动态添加的属性
        attr_keys = request.form.getlist('attr_keys[]')
        attr_values = request.form.getlist('attr_values[]')
        for key, value in zip(attr_keys, attr_values):
            if key:
                properties[key] = value

        try:
            with driver.session() as session:
                session.run(f"CREATE (p:`{label}` $properties) SET p.last_updated = datetime()", properties=properties)
        except Exception as e:
            print(f"Error creating node: {e}")

    nodes = []
    labels = []
    try:
        with driver.session() as session:
            # 构建查询以检索节点
            node_query = "MATCH (n) WHERE n.name CONTAINS $search_query RETURN ID(n) AS id, n.name, labels(n), n.last_updated ORDER BY n.last_updated DESC"
            node_result = session.run(node_query, search_query=search_query)

            # 过滤节点
            for record in node_result:
                node_labels = record["labels(n)"]
                if selected_label and selected_label != "AllLabels" and selected_label not in node_labels:
                    continue
                nodes.append({"id": record["id"], "name": record["n.name"], "labels": node_labels, "last_updated": record["n.last_updated"]})

            # 获取所有独特的标签
            label_query = "CALL db.labels()"
            label_result = session.run(label_query)
            labels = [record["label"] for record in label_result]
    except Exception as e:
        print(f"Error: {e}")

    return render_template('index.html', nodes=nodes, labels=labels, selected_label=selected_label, search_query=search_query)

@app.route('/show/<int:id>', methods=['GET'])
def show(id):
    """显示特定节点的详细信息。"""
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=id)
            data = result.single()
            node = data["n"] if data else None
    except Exception as e:
        print(f"Error retrieving node: {e}")
        node = None

    return render_template('show.html', node=node)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        updated_properties = {key[5:]: value for key, value in request.form.items() if key.startswith("attr_")}
        delete_attrs = request.form.getlist('delete_attrs[]')
        new_attr_keys = request.form.getlist('new_attr_keys[]')
        new_attr_values = request.form.getlist('new_attr_values[]')
        updated_properties.update({key: value for key, value in zip(new_attr_keys, new_attr_values) if key})

        try:
            with driver.session() as session:
                # 更新属性
                for key, value in updated_properties.items():
                    if key not in delete_attrs and key != 'last_updated':
                        query = f"MATCH (n) WHERE ID(n) = $id SET n.`{key}` = $value"
                        session.run(query, id=id, value=value)

                # 删除属性
                for key in delete_attrs:
                    if key != 'name' and key != 'last_updated':
                        query = f"MATCH (n) WHERE ID(n) = $id REMOVE n.`{key}`"
                        session.run(query, id=id)

                # 更新时间戳
                session.run("MATCH (n) WHERE ID(n) = $id SET n.last_updated = datetime()", id=id)

        except Exception as e:
            print(f"Error updating node: {e}")
            return redirect(url_for('index'))  # 如果更新出错，重定向回首页

        return redirect(url_for('show', id=id))  # 更新成功，重定向到展示页面

    # 准备更新页面的初始数据
    node = None
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=id)
            single_result = result.single()
            if single_result:
                node = single_result["n"]
    except Exception as e:
        print(f"Error retrieving node for update: {e}")

    return render_template('update.html', node=node, node_id=id)




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

# 搜索页
@app.route('/searchpage')
def search_page():
    return render_template('search.html')


# 搜索接口
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')  # 获取搜索关键词
    label = request.args.get('label', '')      # 获取可选的标签

    try:
        with driver.session() as session:
            query = "MATCH (n) "
            if label:
                query += f"WHERE '{label}' IN labels(n) AND "
            else:
                query += "WHERE "
            query += "any(prop IN keys(n) WHERE n[prop] CONTAINS $keyword) "
            query += "RETURN n.name, labels(n), ID(n)"
            result = session.run(query, keyword=keyword)
            nodes = [{"name": record["n.name"], "labels": record["labels(n)"], "id": record["ID(n)"]} for record in result]
        return jsonify(nodes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# 定义日期格式化过滤器
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, DateTime):
        value = datetime(
            year=int(value.year),
            month=int(value.month),
            day=int(value.day),
            hour=int(value.hour),
            minute=int(value.minute),
            second=int(value.second)
        )
    elif isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format) if value else ''



if __name__ == '__main__':
    app.run(debug=True, port=5001)
