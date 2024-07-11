from peewee import *


try:
    db = SqliteDatabase('database.db')
    db.connect()
    db.close()
except:
    pass

class User(Model):
    username = CharField(max_length=30, unique=True)
    password = CharField(max_length=160)
    email = CharField(max_length=160, unique=True)
    class Meta:
        database = db

class Tweet(Model):
    user = ForeignKeyField(User, backref='tweets')
    content = CharField(max_length=160)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    class Meta:
        database = db

class Retweet(Model):
    user = ForeignKeyField(User, backref='retweets')
    orig_user = CharField(30)
    created_at = DateTimeField()
    retweeted_at = DateTimeField()
    class Meta:
        database = db

class Follow(Model):
    follower = ForeignKeyField(User, backref='followers')
    following = CharField(30)
    class Meta:
        database = db

def initialize_db(node):
    db.init(f'node_{node.id}.db')
    db.connect()
    db.create_tables([User, Tweet, Retweet, Follow])


