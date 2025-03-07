from typing import List, Optional
from sqlalchemy.orm import Session

from database.models import Email, EmailService
from datetime import datetime

class EmailServiceCRUD:
    @staticmethod
    def create_service(db: Session, email_service: dict) -> EmailService:
        db_service = EmailService(**email_service)
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    @staticmethod
    def get_service(db: Session, email_service_id: str) -> Optional[EmailService]:
        return db.query(EmailService).filter(
            EmailService.email_service_id == email_service_id
        ).first()
    
    # @staticmethod
    # def get_services_by_ids(db: Session, service_ids: List[str]) -> List[EmailService]:
    #     """批量获取服务单
    #     Args:
    #         db: 数据库会话
    #         service_ids: 服务单ID列表
    #     Returns:
    #         List[EmailService]: 服务单列表
    #     """
    #     return db.query(EmailService)\
    #         .filter(EmailService.email_service_id.in_(service_ids))\
    #         .all()

    @staticmethod
    def get_services_by_ids(
        db: Session,
        service_ids: List[str],
        chunk_size: int = 1000
    ) -> List[EmailService]:
        """批量获得服务单数据"""
        if not service_ids:
            return []
        results = []
        for i in range(0, len(service_ids), chunk_size):
            chunk = service_ids[i:i + chunk_size]
            chunk_results = db.query(EmailService).filter(
                EmailService.email_service_id.in_(chunk)
            ).all()
            results.extend(chunk_results)
        
        service_map = {s.email_service_id: s for s in results}
        ordered_services = []
        for service_id in service_ids:
            if service_id in service_map:
                ordered_services.append(service_map[service_id])

        return ordered_services

    @staticmethod
    def get_services(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[EmailService]:
        return db.query(EmailService).offset(skip).limit(limit).all()

    @staticmethod
    def update_service(
        db: Session, 
        email_service_id: str, 
        service_data: dict
    ) -> Optional[EmailService]:
        db_service = db.query(EmailService).filter(
            EmailService.email_service_id == email_service_id
        ).first()
        if db_service:
            for key, value in service_data.items():
                setattr(db_service, key, value)
            db.commit()
            db.refresh(db_service)
        return db_service

    @staticmethod
    def delete_service(db: Session, email_service_id: str) -> bool:
        db_service = db.query(EmailService).filter(
            EmailService.email_service_id == email_service_id
        ).first()
        if db_service:
            db.delete(db_service)
            db.commit()
            return True
        return False

class EmailCRUD:
    @staticmethod
    def create_email(db: Session, email: dict) -> Email:
        db_email = Email(**email)
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
        return db_email

    @staticmethod
    def get_email(db: Session, email_id: str) -> Optional[Email]:
        return db.query(Email).filter(Email.email_id == email_id).first()

    @staticmethod
    def get_emails_by_ids(db: Session, email_ids: List[str]):
        """批量获取邮件"""
        if not email_ids:
            return []
        results = []
        for i in range(0, len(email_ids), 1000):
            chunk = email_ids[i:i + 1000]
            chunk_results = db.query(Email).filter(
                Email.email_id.in_(chunk)
            ).all()
            results.extend(chunk_results)

        email_map = {e.email_id: e for e in results}
        ordered_emails = []
        for email_id in email_ids:
            if email_id in email_map:
                ordered_emails.append(email_map[email_id])

        return ordered_emails


    @staticmethod
    def get_service_emails(
        db: Session, 
        email_service_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Email]:
        return db.query(Email).filter(
            Email.email_service_id == email_service_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_email(
        db: Session, 
        email_id: str, 
        email_data: dict
    ) -> Optional[Email]:
        db_email = db.query(Email).filter(
            Email.email_id == email_id
        ).first()
        if db_email:
            for key, value in email_data.items():
                setattr(db_email, key, value)
            db.commit()
            db.refresh(db_email)
        return db_email

    @staticmethod
    def delete_email(db: Session, email_id: str) -> bool:
        db_email = db.query(Email).filter(
            Email.email_id == email_id
        ).first()
        if db_email:
            db.delete(db_email)
            db.commit()
            return True
        return False