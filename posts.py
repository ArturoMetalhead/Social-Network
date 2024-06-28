from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

class Post(Base):
    __tablename__ = 'posts'

    def __init__(self, text, image, created_at, author):
        self.text = text
        self.image = image
        self.created_at = created_at
        self.author = author

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(160), nullable=True)
    image = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship('User', back_populates='posts')

    def __repr__(self):
        return f"<Post(text='{self.text}', image='{self.image}', created_at='{self.created_at}', author='{self.author.username}')>"