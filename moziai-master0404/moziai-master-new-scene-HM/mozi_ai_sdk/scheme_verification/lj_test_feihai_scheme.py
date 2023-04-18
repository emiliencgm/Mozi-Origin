# a=[1,3]
# b=all([i is not None for i in a])
# print(b)
import xmindparser

# xmindparser配置
# xmindparser配置
xmindparser.config = {
            'showTopicId': False, # 原有配置
            'hideEmptyValue': True, # 原有配置
            'showStructure': False, # 新增配置，是否展示结构值
            'showRelationship': True # 新增配置，是否展示节点关系
        }


filePath = '菲海战事作战方案.xmind'

# 解析成json数据类型
content = xmindparser.xmind_to_json(filePath)

# 解析成dict数据类型
# content = xmindparser.xmind_to_dict(filePath)

# 解析成xml数据类型
# content = xmindparser.xmind_to_xml(filePath)

# 解析到文件
# content = xmindparser.xmind_to_file(filePath, 'json')
# content = xmindparser.xmind_to_file(filePath, 'xml')

print(content)

