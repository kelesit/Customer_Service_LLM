from pydantic import BaseModel, EmailStr, Field


from database.database import get_db
from database.crud import EmailCRUD, EmailServiceCRUD
from database.models import EmailService

from email_service_processor import get_email_service_data

class Email(BaseModel):
    """邮件数据模型"""
    email_id: str = Field(..., description="收件箱ID,邮件的唯一标识")
    email_type: str     # 存疑
    from_name: str  # 发件人姓名
    from_address: EmailStr = Field(..., description="发送人邮箱地址")
    to_name: str # 收件人姓名
    to_address: str # 收件人邮箱
    subject: str = Field(..., description="邮件主题")
    content_preview: str = Field("", description="邮件缩略")    # < 64个字符
    content: str = Field(..., description="邮件内容HTML")
    email_service_id: str = Field(..., description="服务单ID")
    status: str = Field(..., description="邮件状态")    # 用数字表示 TODO: 建立状态字典
    time: str = Field(..., description="邮件创建时间")
    main_content: str = Field("", description="邮件摘要")

    # 存疑且感觉没什么用的属性
    is_star: str
    has_attachment: str     # 是否有附件
    task_flow: str
    user_id: str
    email_template_id: str
    category_id: str
    related_email_id: str
    email_account_id: str
    is_recycle: str
    email_address_book_id: str  # 存疑 "email_address_book_id": "0",
    email_type_id: str  # 存疑 "email_type_id": "0",


    # 以下是目前没有的属性
    order_id: str = Field("", description="订单号")
    long_order_id: str = Field("", description="总订单号")
    original_language: str = Field("", description="邮件原始语种")
    zh_translation: str = Field("", description="邮件中文翻译")
    en_translation: str = Field("", description="邮件英文翻译")
    current_content: str = Field("", description="邮件正文（不包括往来记录）")


    def get_from_db(self, db = None):
        
        """从数据库获取邮件数据"""
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True
            
            try:
                email_data = EmailCRUD.get_email(db, self.email_id)
                if not email_data:
                    return False

                # 使用 Pydantic 的方法更新数据
                updated_data = self.model_validate(email_data)
                self.__dict__.update(updated_data.model_dump())
                return True
            
            finally:
                if should_close_db and db:
                    db.close()

        except Exception as e:
            print(f"获取邮件数据失败: {str(e)}")
            return False
        
    def update_to_db(self, db=None):
        
        """将邮件数据更新到数据库"""
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True
            try:
                update_data = self.model_dump()
                EmailCRUD.update_email(db, self.email_id, update_data)
                print(f"邮件 {self.email_id} 更新成功")
                if should_close_db:
                    db.commit()
                return True
            finally:
                if should_close_db and db:
                    db.close()

        except Exception as e:
            if should_close_db and db:
                db.rollback()
            print(f"更新邮件数据失败: {str(e)}")

    def save_to_db(self, db = None):
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True
            try:
                email_data = EmailCRUD.get_email(db, self.email_id)
                if email_data:
                    EmailCRUD.update_email(db, self.email_id, self.model_dump())
                    #self.update_to_db()
                else:
                    # 先确保服务单存在
                    service = EmailServiceCRUD.get_service(db, self.email_service_id)
                    if not service:
                        print(f"邮件{self.email_id}关联的服务单 {self.email_service_id} 不存在，先创建服务单")
                        print(f'获取服务单数据中')
                        service_data = get_email_service_data(self.email_service_id)
                        service = EmailServiceCRUD.create_service(db, service_data)
                        print(f'服务单 {self.email_service_id} 创建成功')

                    EmailCRUD.create_email(db, self.model_dump())
                if should_close_db:
                    db.commit()
                return True
                # print(f"邮件 {self.email_id} 创建成功")
            finally:
                if should_close_db and db:
                    db.close()

        except Exception as e:
            if should_close_db and db:
                db.rollback()
            print(f"保存邮件数据失败: {str(e)}")