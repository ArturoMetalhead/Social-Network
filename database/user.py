from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.posts import Post
from database.database import Base

followers = Table('followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False)
    password = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    following = relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='followers'
    )
    posts = relationship('Post', back_populates='author')


    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return user in self.following

    def followers_count(self):
        return len(self.followers)
    
    def following_count(self):
        return len(self.following)
    
    def upload_post(self, session, text=None, image=None):
        new_post = Post(text=text, image=image, created_at=datetime.now(timezone.utc), author=self)
        session.add(new_post)
        return new_post
    
    def get_posts(self):
        print(self.posts.__repr__())