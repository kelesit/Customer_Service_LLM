from pydantic import BaseModel, Field
from datetime import datetime

from database.database import get_db
from database.crud import EmailServiceCRUD


class Email_Service(BaseModel):
    """服务单数据模型"""
    email_service_id: str = Field(..., description='服务单ID')
    customer_address: str = Field(..., description='顾客邮箱地址')
    email_account_id: str   # 存疑
    title: str = Field(..., description='服务单标题')
    status: str = Field(..., description='状态')     # 存疑 TODO: 建立状态字典？
    add_time: datetime = Field(..., description='创建时间')
    type: str = Field(..., description='服务单类型')
    email_list: list = Field(default=[], description='邮件列表')
    p_type: str | None = Field(default=None, description='预测类别')

    class Config:
        from_attributes = True
        
    def get_from_db(self, db = None):
        """从数据库获取服务单数据"""
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True

            try:
                service_data = EmailServiceCRUD.get_service(db, self.email_service_id)
                if not service_data:
                    return False
                
                # 使用 Pydantic 的方法更新数据
                updated_data = self.model_validate(service_data)
                self.__dict__.update(updated_data.model_dump())
                return True
            finally:
                if should_close_db and db:
                    db.close()
            
        except Exception as e:
            if should_close_db and db:
                db.rollback()
            print(f"获取服务单数据失败: {str(e)}")
            return False
        


    def update_to_db(self, db = None):
        """将服务单数据更新到数据库"""
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True
            try:
                update_data = self.model_dump()
                EmailServiceCRUD.update_service(db, self.email_service_id, update_data)
                print(f"服务单 {self.email_service_id} 更新成功")
                if should_close_db:
                    db.commit()
                return True
            finally:
                if should_close_db and db:
                    db.close()

        except Exception as e:
            if should_close_db and db:
                db.rollback()
            print(f"更新服务单数据失败: {str(e)}")


    def save_to_db(self, db=None):
        """将服务单数据保存到数据库"""
        try:
            should_close_db = False
            if db is None:
                db = next(get_db())
                should_close_db = True

            try:
                service_data = EmailServiceCRUD.get_service(db, self.email_service_id)
                if service_data:
                    EmailServiceCRUD.update_service(db, self.email_service_id, self.model_dump())
                    # self.update_to_db()
                else:
                    EmailServiceCRUD.create_service(db, self.model_dump())

                if should_close_db:
                    db.commit()
                return True
            finally:
                if should_close_db and db:
                    db.close()
                # print(f"服务单 {self.email_service_id} 创建成功")
        except Exception as e:
            if should_close_db and db:
                db.rollback()
            print(f"保存服务单数据失败: {str(e)}")