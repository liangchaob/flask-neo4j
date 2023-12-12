// 创建企业节点
CREATE (CompanyA:企业 {name: '华夏制造', 注册资本: '5000万', 社会信用编号: '1234567890ABC', 基本介绍: '专业生产工业机械'})
CREATE (CompanyB:企业 {name: '东方电子', 注册资本: '8000万', 社会信用编号: '0987654321XYZ', 基本介绍: '高新技术电子产品制造商'})

// 创建区域节点
CREATE (RegionX:区域 {name: '江南省', 区域简介: '经济发达，工业基础雄厚', 区域坐标: '23.5, 115.5'})
CREATE (RegionY:区域 {name: '北方市', 区域简介: '服务业为主导，经济多元化', 区域坐标: '42.1, 120.3'})

// 创建政策节点
CREATE (Policy1:政策 {name: '创新资助计划', 政策详情: '支持科技创新企业', 政策类型: '科技', 颁发部门: '江南省政府', 颁发日期: '2023-01-01'})
CREATE (Policy2:政策 {name: '绿色制造扶持', 政策详情: '促进绿色环保产业发展', 政策类型: '环保', 颁发部门: '北方市政府', 颁发日期: '2023-02-01'})

// 创建产品节点
CREATE (Product1:产品 {name: '智能机器人', 基本介绍: '用于自动化生产线', 所属行业: '机器人制造'})
CREATE (Product2:产品 {name: '太阳能电池板', 基本介绍: '高效清洁能源产品', 所属行业: '新能源'})

// 创建边的关系
CREATE
(CompanyA)-[:注册地]->(RegionX),
(CompanyB)-[:注册地]->(RegionY),
(RegionX)-[:颁发]->(Policy1),
(RegionY)-[:颁发]->(Policy2),
(CompanyA)-[:生产]->(Product1),
(CompanyB)-[:生产]->(Product2),
(Policy1)-[:促进]->(Product1),
(Policy2)-[:激励]->(Product2)
// 扩展企业节点
CREATE (CompanyC:企业 {name: '远东通信', 注册资本: '10000万', 社会信用编号: '555666777888', 基本介绍: '通信设备制造商'})
CREATE (CompanyD:企业 {name: '北辰软件', 注册资本: '6000万', 社会信用编号: '999888777666', 基本介绍: '软件开发与服务'})

// 扩展区域节点
CREATE (RegionZ:区域 {name: '西部高原', 区域简介: '资源丰富，生态环保', 区域坐标: '35.2, 101.1'})
CREATE (RegionW:区域 {name: '东海岸', 区域简介: '贸易发达，经济开放', 区域坐标: '31.4, 121.5'})

// 扩展政策节点
CREATE (Policy3:政策 {name: '软件产业扶持政策', 政策详情: '提升软件产业国际竞争力', 政策类型: '产业', 颁发部门: '国家科技部', 颁发日期: '2023-03-01'})
CREATE (Policy4:政策 {name: '高新技术企业认定', 政策详情: '支持高新技术企业发展', 政策类型: '技术', 颁发部门: '国家发改委', 颁发日期: '2023-04-01'})

// 扩展产品节点
CREATE (Product3:产品 {name: '虚拟现实头盔', 基本介绍: '高端VR游戏体验', 所属行业: '虚拟现实'})
CREATE (Product4:产品 {name: '智能穿戴设备', 基本介绍: '健康监测与生活助手', 所属行业: '智能硬件'})

// 扩展边的关系
CREATE
(CompanyC)-[:注册地]->(RegionZ),
(CompanyD)-[:注册地]->(RegionW),
(RegionZ)-[:颁发]->(Policy3),
(RegionW)-[:颁发]->(Policy4),
(CompanyC)-[:生产]->(Product3),
(CompanyD)-[:生产]->(Product4),
(Policy3)-[:促进]->(Product3),
(Policy4)-[:激励]->(Product4)

// 继续添加企业节点
CREATE (CompanyE:企业 {name: '新光能源', 注册资本: '12000万', 社会信用编号: '222333444555', 基本介绍: '太阳能产品制造'})
CREATE (CompanyF:企业 {name: '蓝海科技', 注册资本: '9500万', 社会信用编号: '555444333222', 基本介绍: '海洋技术开发与研究'})
// ... 更多企业

// 继续添加区域节点
CREATE (RegionV:区域 {name: '中原市', 区域简介: '历史悠久，文化底蕴深厚', 区域坐标: '34.6, 113.7'})
CREATE (RegionU:区域 {name: '南岛省', 区域简介: '旅游胜地，生物多样性', 区域坐标: '18.2, 109.5'})
// ... 更多区域

// 继续添加政策节点
CREATE (Policy5:政策 {name: '旅游业发展支持', 政策详情: '鼓励发展旅游相关产业', 政策类型: '旅游', 颁发部门: '南岛省政府', 颁发日期: '2023-05-01'})
CREATE (Policy6:政策 {name: '环保产业激励措施', 政策详情: '促进环保技术创新和应用', 政策类型: '环保', 颁发部门: '国家环保局', 颁发日期: '2023-06-01'})
// ... 更多政策

// 继续添加产品节点
CREATE (Product5:产品 {name: '自动化包装机', 基本介绍: '用于食品和药品行业', 所属行业: '自动化设备'})
CREATE (Product6:产品 {name: '生物识别系统', 基本介绍: '安全识别技术', 所属行业: '信息安全'})
// ... 更多产品

// 继续添加边的关系
CREATE
(CompanyE)-[:注册地]->(RegionV),
(CompanyF)-[:注册地]->(RegionU),
(RegionV)-[:颁发]->(Policy5),
(RegionU)-[:颁发]->(Policy6),
(CompanyE)-[:生产]->(Product5),
(CompanyF)-[:生产]->(Product6),
(Policy5)-[:促进]->(Product5),
(Policy6)-[:激励]->(Product6)
// ... 更多关系

// 重复以上步骤，直到达到400条以上数据量

// 继续生成企业节点
CREATE (CompanyG:企业 {name: '明云数据', 注册资本: '11000万', 社会信用编号: 'ABCDEF123456', 基本介绍: '云计算服务提供商'})
CREATE (CompanyH:企业 {name: '九州机械', 注册资本: '7500万', 社会信用编号: 'XYZ987654321', 基本介绍: '重型机械制造'})

// 继续生成区域节点
CREATE (RegionS:区域 {name: '港城市', 区域简介: '国际贸易港口', 区域坐标: '22.3, 113.6'})
CREATE (RegionT:区域 {name: '云边市', 区域简介: '高科技产业集聚区', 区域坐标: '25.0, 102.7'})

// 继续生成政策节点
CREATE (Policy7:政策 {name: '高端制造业发展', 政策详情: '加强高端制造业扶持', 政策类型: '制造业', 颁发部门: '工业和信息化部', 颁发日期: '2023-07-01'})
CREATE (Policy8:政策 {name: '文化产业振兴计划', 政策详情: '促进文化产业发展', 政策类型: '文化', 颁发部门: '文化部', 颁发日期: '2023-08-01'})

// 继续生成产品节点
CREATE (Product7:产品 {name: '高效电动汽车', 基本介绍: '新能源汽车制造', 所属行业: '新能源汽车'})
CREATE (Product8:产品 {name: '智能家居系统', 基本介绍: '家居自动化控制系统', 所属行业: '智能家居'})

// 继续添加边的关系
CREATE
(CompanyG)-[:注册地]->(RegionS),
(CompanyH)-[:注册地]->(RegionT),
(RegionS)-[:颁发]->(Policy7),
(RegionT)-[:颁发]->(Policy8),
(CompanyG)-[:生产]->(Product7),
(CompanyH)-[:生产]->(Product8),
(Policy7)-[:促进]->(Product7),
(Policy8)-[:激励]->(Product8)

// 更多数据生成中...
// 生成新的产品节点
CREATE (Product9:产品 {name: '智能机器臂', 基本介绍: '工业自动化核心部件', 所属行业: '机器人'})
CREATE (Product10:产品 {name: '光纤通信线缆', 基本介绍: '高速光纤传输产品', 所属行业: '通信设备'})
CREATE (Product11:产品 {name: '人工智能芯片', 基本介绍: '用于各类智能设备的核心芯片', 所属行业: '半导体'})
CREATE (Product12:产品 {name: '精密医疗仪器', 基本介绍: '医疗诊断精密仪器', 所属行业: '医疗设备'})

// 定义产品的上下游关系
CREATE
(Product9)-[:上游产品]->(Product1),
(Product10)-[:下游产品]->(Product2),
(Product11)-[:上游产品]->(Product3),
(Product12)-[:下游产品]->(Product4)

// 定义产品的上下级关系
CREATE
(Product9)-[:子产品]->(Product5),
(Product10)-[:子产品]->(Product6),
(Product11)-[:母产品]->(Product7),
(Product12)-[:母产品]->(Product8)

// 将新产品与企业关联
CREATE
(CompanyA)-[:生产]->(Product9),
(CompanyB)-[:生产]->(Product10),
(CompanyC)-[:生产]->(Product11),
(CompanyD)-[:生产]->(Product12)

// 将新产品与政策关联
CREATE
(Policy3)-[:促进]->(Product9),
(Policy4)-[:激励]->(Product10),
(Policy5)-[:促进]->(Product11),
(Policy6)-[:激励]->(Product12)

// 连接产品与区域
CREATE
(RegionX)-[:规划]->(Product9),
(RegionY)-[:规划]->(Product10),
(RegionZ)-[:规划]->(Product11),
(RegionW)-[:规划]->(Product12)

// 更多数据生成中...
// 生成新的产品节点
CREATE (Product13:产品 {name: '先进机器视觉系统', 基本介绍: '用于自动化检测与控制', 所属行业: '机器视觉'})
CREATE (Product14:产品 {name: '环保型电池', 基本介绍: '绿色能源储存解决方案', 所属行业: '新能源'})
CREATE (Product15:产品 {name: '智慧城市管理平台', 基本介绍: '城市管理和服务一体化平台', 所属行业: '智慧城市'})
CREATE (Product16:产品 {name: '生物医药新药', 基本介绍: '创新型生物医药产品', 所属行业: '生物医药'})

// 定义产品的上下游关系
CREATE
(Product13)-[:上游产品]->(Product5),
(Product14)-[:下游产品]->(Product6),
(Product15)-[:上游产品]->(Product7),
(Product16)-[:下游产品]->(Product8)

// 定义产品的上下级关系
CREATE
(Product13)-[:子产品]->(Product9),
(Product14)-[:子产品]->(Product10),
(Product15)-[:母产品]->(Product11),
(Product16)-[:母产品]->(Product12)

// 将新产品与企业关联
CREATE
(CompanyE)-[:生产]->(Product13),
(CompanyF)-[:生产]->(Product14),
(CompanyG)-[:生产]->(Product15),
(CompanyH)-[:生产]->(Product16)

// 将新产品与政策关联
CREATE
(Policy7)-[:促进]->(Product13),
(Policy8)-[:激励]->(Product14),
(Policy1)-[:促进]->(Product15),
(Policy2)-[:激励]->(Product16)

// 连接产品与区域
CREATE
(RegionS)-[:规划]->(Product13),
(RegionT)-[:规划]->(Product14),
(RegionV)-[:规划]->(Product15),
(RegionU)-[:规划]->(Product16)
