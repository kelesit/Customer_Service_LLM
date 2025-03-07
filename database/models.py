from datetime import datetime, timezone
from typing import List
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, Mapped

import sys
import os

current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)

from database.database import Base


class EmailService(Base):
    """服务单数据库模型"""
    __tablename__ = 'email_services'

    email_service_id = Column(String(50), primary_key=True, comment='服务单ID')
    customer_address = Column(String(255), nullable=False, comment='顾客邮箱地址')
    email_account_id = Column(String(50), comment='邮件账户ID')
    title = Column(String(255), nullable=False, comment='服务单标题')
    status = Column(String(20), nullable=False, comment='状态')
    add_time = Column(DateTime, default=datetime.now(timezone.utc), comment='创建时间')
    type = Column(String(50), nullable=False, comment='服务单类型')
    email_list = Column(JSON, comment='邮件列表原始数据')
    p_type = Column(String(50), nullable=True, comment='预测类别')
    
    # 建立与Email的一对多关系
    # 由于邮件必须依赖于服务单存在，因此在删除服务单时，也应删除其关联的所有邮件
    # 因此使用cascade="all, delete-orphan"来实现级联删除
    emails: Mapped[List["Email"]] = relationship("Email", back_populates="service", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "email_service_id": self.email_service_id,
            "customer_address": self.customer_address,
            "email_account_id": self.email_account_id,
            "title": self.title,
            "status": self.status,
            "add_time": self.add_time,
            "type": self.type,
            "p_type": self.p_type,
            "email_list": self.email_list,
        }


class Email(Base):
    """邮件数据库模型"""
    __tablename__ = 'emails'

    email_id = Column(String(50), primary_key=True, comment='收件箱ID,邮件的唯一标识')
    email_type = Column(String(50))
    from_name = Column(String(255), comment='发件人姓名')
    from_address = Column(String(255), nullable=False, comment='发送人邮箱地址')
    to_name = Column(String(255), comment='收件人姓名')
    to_address = Column(String(255), nullable=False, comment='收件人邮箱')
    subject = Column(String(255), nullable=False, comment='邮件主题')
    content_preview = Column(String(500), comment='邮件缩略')
    content = Column(Text(length=4294967295), nullable=False, comment='邮件内容HTML')
    status = Column(String(20), nullable=False, comment='邮件状态')
    time = Column(DateTime, default=datetime.now(timezone.utc), comment='邮件创建时间')
    main_content = Column(Text, comment='邮件摘要')
    
    # 可选字段
    is_star = Column(String(1), default=False, comment='是否星标')
    has_attachment = Column(String(1), default=False, comment='是否有附件')
    task_flow = Column(String(50))
    user_id = Column(String(50))
    email_template_id = Column(String(50))
    category_id = Column(String(50))
    related_email_id = Column(String(50))
    is_recycle = Column(String(1), default=False)
    email_address_book_id = Column(String(50))
    email_type_id = Column(String(50))
    email_account_id = Column(String(50))
    
    # 新增字段
    order_id = Column(String(50), comment='订单号')
    long_order_id = Column(String(50), comment='总订单号')
    original_language = Column(String(20), comment='邮件原始语种')
    zh_translation = Column(Text, comment='邮件中文翻译')
    en_translation = Column(Text, comment='邮件英文翻译')
    current_content = Column(Text, comment='邮件正文')
    
    # 外键关联
    email_service_id = Column(String(50), ForeignKey('email_services.email_service_id'), nullable=False)
    service = relationship("EmailService", back_populates="emails")


    def to_dict(self):
        return {
            "email_id": self.email_id,
            "email_type": self.email_type,
            "from_name": self.from_name,
            "from_address": self.from_address,
            "to_name": self.to_name,
            "to_address": self.to_address,
            "subject": self.subject,
            "content_preview": self.content_preview,
            "content": self.content,
            "status": self.status,
            "time": self.time,
            "is_star": self.is_star,
            "has_attachment": self.has_attachment,
            "task_flow": self.task_flow,
            "user_id": self.user_id,
            "email_template_id": self.email_template_id,
            "category_id": self.category_id,
            "related_email_id": self.related_email_id,
            "is_recycle": self.is_recycle,
            "email_address_book_id": self.email_address_book_id,
            "email_type_id": self.email_type_id,
            "email_account_id": self.email_account_id,
            "order_id": self.order_id,
            "long_order_id": self.long_order_id,
            "original_language": self.original_language,
            "zh_translation": self.zh_translation,
            "en_translation": self.en_translation,
            "current_content": self.current_content,
            "email_service_id": self.email_service_id,
        }
    
    

"""
# 从服务单访问邮件
service = EmailService.get(service_id)
for email in service.emails:
    print(email.subject)

# 从邮件访问服务单
email = Email.get(email_id)
print(email.service.title)
"""