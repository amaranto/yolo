from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

from config import logging, PROJECT, REGION, SQL_INSTANCE, SQL_USER, SQL_PWD, SQL_DB, SQL_ENABLE_IAM

sql_instance = f"{PROJECT}:{REGION}:{SQL_INSTANCE}" 
connector = Connector(IPTypes.PRIVATE)

def getconn(
    instance_connection_name: str = sql_instance,  # <PROJECT-ID>:<REGION>:<INSTANCE-NAME>
    engine: str = "pymysql",
    user: str|None = SQL_USER, 
    password: str|None = SQL_PWD, 
    db: str|None = SQL_DB, 
    enable_iam: bool = SQL_ENABLE_IAM):
    
    conn = None
    
    if enable_iam:
        conn = connector.connect(
            instance_connection_name,
            engine,
            db=db,
            enable_iam=True
        )
    elif user and password:
        conn = connector.connect(
            instance_connection_name,
            engine,
            user=user,
            password=password,
            db=db
        )
    else:
        raise ValueError("Please provide user and password or enable_iam=True")
    
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)