# 客服

## Setup

.ENV配置

```shell
OPENAI_API_KEY = "sk-xxx"
QWEN_API_KEY = "sk-yyyy"
```

## 项目结构说明

重要代码文件:
email_service_processor.py: 服务单处理器，包括服务单数据获取、...
email_processor.py: 邮件处理器，包括邮件数据获取、llm解析邮件流程、...
script/customer_service_llm.py: llm自主介入客服工作流demo

数据类型： 存放数据模型，包括邮件、服务单
data_structure/

服务单分析：
email_service_analysis/

数据库:
database/
database.py: 数据库连接与配置
models.py: 数据库模型
crud.py: 数据库操作
test.py: 测试数据库操作

脚本文件：
script/
update_email_service_to_db.py: 更新服务单到数据库
update_email_to_db.py: 更新邮件到数据库
customer_service_llm.py: llm自主介入客服工作流demo

工具：
utils/
chat.py: 与llm交互
tools.py: 工具函数 (如：邮件正文提取、...)
