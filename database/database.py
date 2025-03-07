from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 数据库连接配置
HOST = '192.168.100.33'
PORT = '3306'
USER = 'zhenggantian'
PASSWORD = '123456'
DATABASE = 'workflow'

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 连接池大小
    max_overflow=5,        # 超过连接池大小外最多创建的连接数
    pool_recycle=3600     # 连接重置周期（秒）
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    获取数据库会话
    使用示例:
    db = next(get_db())
    try:
        # 使用db进行数据库操作
        pass
    finally:
        db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库表"""
    from models import Email, EmailService
    print("发现的数据模型:")
    for table in Base.metadata.tables:
        print(f"- {table}")
    print("\n开始创建表...")
    Base.metadata.create_all(bind=engine)
    print("表创建完成!")