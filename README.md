# flask-neo4j

这个项目是一个基于 Flask 和 Neo4j 的简单应用，它提供了一个基本的框架来展示如何在 Web 应用中实现对 Neo4j 数据库的 CRUD（创建、读取、更新、删除）操作。

## 基本功能

* **搜索节点** ：用户可以按属性关键字或者标签搜索节点。
* **创建节点** ：用户可以创建具有特定标签和属性的新节点。
* **读取节点** ：用户可以查看数据库中所有节点的列表，包括它们的名称和标签。
* **更新节点** ：用户可以更新特定节点的属性。
* **删除节点** ：用户可以删除特定节点。
* **查看标签** ：用户可以查看数据库中所有唯一标签的列表。

![demo](http://ipic-liangchao.test.upcdn.net/demo.gif)

## 初始配置方法

### 环境要求

* Python 3.6 或更高版本
* Flask
* Neo4j Python Driver
* 一个运行中的 Neo4j 数据库实例

### 安装步骤

1. **克隆仓库** ：

```
git clone https://github.com/liangchaob/flask-neo4j.git
```

2. **安装依赖** ：
   在项目根目录下运行：

```
pip install -r requirements.txt
```

3. **配置环境变量** ：
   创建一个 `config.py` 文件，并设置以下变量：

```
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='password'
```

4. **运行应用** ：

```
python app.py
```

### 连接到 Neo4j 数据库

确保您的 Neo4j 数据库正在运行，并且您已经在 `config.py` 文件中正确设置了数据库的用户名和密码。应用将使用这些凭据连接到数据库。

- **示例数据** ：
  示例数据保存在 `demo_data` 中，通过Neo4j Blowser执行后即可插入数据库

## 使用说明

* 访问 `http://localhost:5001/` 来启动应用。
* 使用提供的界面创建、查看、更新或删除节点。
* 访问 `/labels` 路径以查看数据库中所有的标签。
