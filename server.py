from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

user_server_association = Table('user_server_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('server_id', Integer, ForeignKey('servers.id'))
)

post_server_association = Table('post_server_association', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('server_id', Integer, ForeignKey('servers.id')))

class Server(Base):
    __tablename__ = 'servers'

    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    ip = Column(String(20), nullable=False)
    port = Column(Integer, nullable=False)
    users = relationship('User', secondary=user_server_association, back_populates='servers')
    posts = relationship('Post', secondary=post_server_association, back_populates='servers')
