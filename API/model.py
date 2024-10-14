import peewee
import hashlib
import datetime
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField, ForeignKeyField, DateTimeField

try:
    main_db = SqliteDatabase('social_network.db')
    main_db.connect()
    main_db.close()
except:
    pass

class User(Model):
    name = CharField(120)
    alias = CharField(16, unique=True)
    password = CharField(64)
    alias_hash = CharField(64)
    class Meta:
        database = main_db

class Follow(Model):
    follower = ForeignKeyField(User)
    followed =  CharField(16)

    class Meta:
        database = main_db  

class Tweet(Model):
    text = CharField(256)
    user = ForeignKeyField(User)
    date = DateTimeField(default=datetime.datetime.now())
    class Meta:
        database = main_db

#main_db.create_tables([User, Follow, Tweet, ReTweet, Token])