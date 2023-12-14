from flask import Flask, render_template, request, redirect, url_for, jsonify
from neo4j import GraphDatabase, exceptions
from config import NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_HOST, NEO4J_PORT
from datetime import datetime
from neo4j.time import DateTime
from math import ceil  # 导入向上取整函数

app = Flask(__name__)

# 初始化 Neo4j 数据库连接
uri = "bolt://"+ NEO4J_HOST + ":" + NEO4J_PORT
try:
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
except exceptions.ServiceUnavailable as e:
    raise SystemExit("Failed to connect to Neo4j database.") from e

# 设置每页显示的节点数量
PER_PAGE_LIMIT = 20


@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/filter/<selected_label>', methods=['GET'])
def index(selected_label=None):
    """处理首页的请求，显示所有节点或根据标签过滤节点。"""
    search_query = request.args.get('search', '')  # 获取搜索查询参数
    page = int(request.args.get('page', 1))  # 获取当前页码
    
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
            # 构建基础查询
            base_query = "MATCH (n)"
            if selected_label and selected_label != "AllLabels":
                base_query += f" WHERE '{selected_label}' IN labels(n)"

            # 添加搜索条件
            if search_query:
                base_query += f" AND n.name CONTAINS $search_query"

            # 查询总节点数
            count_query = base_query + " RETURN count(n) as total"
            total_count_result = session.run(count_query, search_query=search_query)
            total_count = total_count_result.single()["total"]

            # 计算总页数
            total_pages = (total_count + PER_PAGE_LIMIT - 1) // PER_PAGE_LIMIT

            # 分页查询节点
            skip = (page - 1) * PER_PAGE_LIMIT
            node_query = base_query + " RETURN ID(n) AS id, n.name, labels(n), n.last_updated ORDER BY n.last_updated DESC SKIP $skip LIMIT $limit"
            node_result = session.run(node_query, search_query=search_query, skip=skip, limit=PER_PAGE_LIMIT)

            nodes = [{"id": record["id"], "name": record["n.name"], "labels": record["labels(n)"], "last_updated": record["n.last_updated"]} for record in node_result]

            # 获取每个标签及其对应的节点数
            labels_result = session.run("MATCH (n) UNWIND labels(n) AS label RETURN label, COUNT(n) AS count")
            labels_with_counts = [{"label": record["label"], "count": record["count"]} for record in labels_result]

    except Exception as e:
        print(f"Error: {e}")

    return render_template('admin.html', nodes=nodes, labels_with_counts=labels_with_counts, selected_label=selected_label, search_query=search_query, total_pages=total_pages, current_page=page)

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
                "RETURN TYPE(r) AS type, ID(r) AS relation_id, ID(m) AS target_id, m.name AS target_name", 
                id=id
            )

            # 获取节点的所有入站关系（即节点是关系的终点）
            incoming_rels = session.run(
                "MATCH (n)<-[r]-(m) WHERE ID(n) = $id "
                "RETURN TYPE(r) AS type, ID(r) AS relation_id, ID(m) AS source_id, m.name AS source_name", 
                id=id
            )

            # 合并这两个结果
            relationships = [
                {"type": record["type"], "relation_id": record["relation_id"], "target_id": record["target_id"], "target_name": record["target_name"], "direction": "outgoing"}
                for record in outgoing_rels
            ]
            relationships += [
                {"type": record["type"], "relation_id": record["relation_id"], "source_id": record["source_id"], "source_name": record["source_name"], "direction": "incoming"}
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
    keyword = request.args.get('keyword', '')
    label = request.args.get('label', '')
    page = int(request.args.get('page', 1))  # 当前页码，默认为第一页
    limit = int(request.args.get('limit', 10))  # 每页节点数量，默认为10

    skip = (page - 1) * limit  # 计算跳过的节点数量

    try:
        with driver.session() as session:
            # 首先计算总节点数
            count_query = "MATCH (n) WHERE any(prop IN keys(n) WHERE n[prop] CONTAINS $keyword) "
            if label:
                count_query += f"AND '{label}' IN labels(n) "
            count_query += "RETURN count(n) as total"
            count_result = session.run(count_query, keyword=keyword)
            total_nodes = count_result.single()[0]

            # 计算总页数
            total_pages = ceil(total_nodes / limit)

            # 接着获取特定页面的节点数据
            node_query = "MATCH (n) WHERE any(prop IN keys(n) WHERE n[prop] CONTAINS $keyword) "
            if label:
                node_query += f"AND '{label}' IN labels(n) "
            node_query += "RETURN n.name, labels(n), ID(n) ORDER BY n.name SKIP $skip LIMIT $limit"
            node_result = session.run(node_query, keyword=keyword, skip=skip, limit=limit)
            nodes = [{"name": record["n.name"], "labels": record["labels(n)"], "id": record["ID(n)"]} for record in node_result]

            # 返回节点数据和分页信息
            return jsonify({
                "nodes": nodes,
                "totalPages": total_pages,
                "currentPage": page
            })
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
                f"MERGE (n)-[r:`{relation_type}`]->(m)", 
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

# 删除关系
@app.route('/delete_relationship', methods=['POST'])
def delete_relationship():
    relation_id = request.form.get('relation_id')
    node_id = request.form.get('node_id')
    direction = request.form.get('direction')

    # 确保 ID 是整数
    try:
        relation_id = int(relation_id)
        node_id = int(node_id)
    except ValueError:
        print("Invalid relation_id or node_id")
        return redirect(url_for('update', id=node_id))

    print(f"Deleting relationship: {relation_id}, Node ID: {node_id}, Direction: {direction}")

    try:
        with driver.session() as session:
            if direction == 'outgoing':
                print("Deleting outgoing relationship")
                result = session.run("MATCH (n)-[r]->() WHERE ID(n) = $node_id AND ID(r) = $relation_id DELETE r RETURN r",
                            node_id=node_id, relation_id=relation_id)
                print(f"Deleted relationships: {result.summary().counters.relationships_deleted}")
            elif direction == 'incoming':
                print("Deleting incoming relationship")
                result = session.run("MATCH ()-[r]->(n) WHERE ID(n) = $node_id AND ID(r) = $relation_id DELETE r RETURN r",
                            node_id=node_id, relation_id=relation_id)
                print(f"Deleted relationships: {result.summary().counters.relationships_deleted}")
    except Exception as e:
        print(f"Error deleting relationship: {e}")

    return redirect(url_for('update', id=node_id))







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