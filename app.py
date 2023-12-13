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

@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/filter/<selected_label>', methods=['GET'])
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
    labels_with_counts = []
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

            # 获取每个标签及其对应的节点数
            labels_result = session.run("MATCH (n) UNWIND labels(n) AS label RETURN label, COUNT(n) AS count")
            labels_with_counts = [{"label": record["label"], "count": record["count"]} for record in labels_result]

    except Exception as e:
        print(f"Error: {e}")

    return render_template('admin.html', nodes=nodes, labels_with_counts=labels_with_counts, selected_label=selected_label, search_query=search_query)

@app.route('/show/<int:id>', methods=['GET'])
def show(id):
    """显示特定节点的详细信息和相关边。"""
    try:
        with driver.session() as session:
            # 获取节点信息
            node_query = "MATCH (n) WHERE ID(n) = $id RETURN n"
            node_result = session.run(node_query, id=id)
            node_data = node_result.single()
            node = node_data["n"] if node_data else None

            # 获取与节点相关的双向边信息
            edges_query = """
            MATCH (n)-[r]->(m) WHERE ID(n) = $id 
            RETURN type(r) as type, collect({id: ID(m), name: m.name, labels: labels(m)}) as targets, 'outgoing' as direction
            UNION
            MATCH (n)<-[r]-(m) WHERE ID(n) = $id 
            RETURN type(r) as type, collect({id: ID(m), name: m.name, labels: labels(m)}) as targets, 'incoming' as direction
            """
            edges_result = session.run(edges_query, id=id)
            edges = [{"type": record["type"], "targets": record["targets"], "direction": record["direction"]} for record in edges_result]

    except Exception as e:
        print(f"Error retrieving node or edges: {e}")
        node = None
        edges = []

    return render_template('show.html', node=node, edges=edges)



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
    relationships = []
    try:
        with driver.session() as session:
            # 获取节点信息
            node_result = session.run("MATCH (n) WHERE ID(n) = $id RETURN n", id=id)
            node_data = node_result.single()
            if node_data:
                node = node_data["n"]

            # 获取节点的所有出站关系（即节点是关系的起点）
            outgoing_rels = session.run(
                "MATCH (n)-[r]->(m) WHERE ID(n) = $id "
                "RETURN TYPE(r) AS type, ID(m) AS target_id, m.name AS target_name", 
                id=id
            )

            # 获取节点的所有入站关系（即节点是关系的终点）
            incoming_rels = session.run(
                "MATCH (n)<-[r]-(m) WHERE ID(n) = $id "
                "RETURN TYPE(r) AS type, ID(m) AS source_id, m.name AS source_name", 
                id=id
            )

            # 合并这两个结果
            relationships = [
                {"type": record["type"], "target_id": record["target_id"], "target_name": record["target_name"], "direction": "outgoing"}
                for record in outgoing_rels
            ]
            relationships += [
                {"type": record["type"], "source_id": record["source_id"], "source_name": record["source_name"], "direction": "incoming"}
                for record in incoming_rels
            ]

    except Exception as e:
        print(f"Error: {e}")

    return render_template('update.html', node=node, node_id=id, relationships=relationships)


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """删除特定节点。"""
    try:
        with driver.session() as session:
            session.run("MATCH (n) WHERE ID(n) = $id DETACH DELETE n", id=id)
    except Exception as e:
        print(f"Error deleting node: {e}")

    return redirect(url_for('index'))


# 将搜索页面设为主页
@app.route('/')
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


@app.route('/labels')
def get_labels():
    try:
        with driver.session() as session:
            result = session.run("CALL db.labels()")
            labels_with_counts = []
            for record in result:
                label = record["label"]
                count_result = session.run(f"MATCH (n:`{label}`) RETURN count(n) as count")
                count = count_result.single()["count"]
                labels_with_counts.append({"label": label, "count": count})
            return jsonify(labels_with_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update_relationship/<int:id>', methods=['POST'])
def update_relationship(id):
    relation_type = request.form['relation_type']
    target_id = int(request.form['target_id'])

    try:
        with driver.session() as session:
            # 添加新关系
            session.run(
                "MATCH (n), (m) WHERE ID(n) = $node_id AND ID(m) = $target_id "
                "MERGE (n)-[r:`{relation_type}`]->(m)", 
                node_id=id, target_id=target_id, relation_type=relation_type
            )
    except Exception as e:
        print(f"Error updating relationship: {e}")

    return redirect(url_for('update', id=id))

# 按照名称搜索节点
@app.route('/search_nodes', methods=['GET'])
def search_nodes():
    query = request.args.get('query', '')

    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n.name CONTAINS $queryParam RETURN ID(n) AS id, n.name LIMIT 10", 
                queryParam=query
            )
            nodes = [{"id": record["id"], "name": record["n.name"]} for record in result]
        return jsonify(nodes)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# TODO
@app.route('/delete_relationship', methods=['POST'])
def delete_relationship():
    from_id = request.form.get('from_id')
    to_id = request.form.get('to_id')
    relation_type = request.form.get('relation_type')

    try:
        with driver.session() as session:
            session.run(
                "MATCH (from)-[r:`{relation_type}`]->(to) "
                "WHERE ID(from) = $from_id AND ID(to) = $to_id "
                "DELETE r",
                from_id=int(from_id), to_id=int(to_id), relation_type=relation_type
            )
        return redirect(url_for('show', id=from_id))
    except Exception as e:
        print(f"Error deleting relationship: {e}")
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