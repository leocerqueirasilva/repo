
from apps import db
from datetime import datetime
from pytz import timezone
from flask import Flask



class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    setting = db.Column(db.String(1020))


    

    

    def to_dict(self):
        return {'username': self.username}


class LikeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone('America/Sao_Paulo')))
    media_url = db.Column(db.String(255))
    num_accounts = db.Column(db.Integer)



class CommentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone('America/Sao_Paulo')))
    media_url = db.Column(db.String(256))
    num_comments = db.Column(db.Integer)
    comment_text = db.Column(db.String(256))



class FollowHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_username = db.Column(db.String(120), nullable=False)
    num_followers = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone('America/Sao_Paulo')))

    def __repr__(self):
        return f'<FollowHistory {self.target_username}>'
    

class VoteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone('America/Sao_Paulo')))
    media_url = db.Column(db.String, nullable=False)
    vote_option = db.Column(db.String, nullable=False)
    num_accounts = db.Column(db.Integer, nullable=False)



class StoryLikeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_url = db.Column(db.String(500), nullable=False)
    num_accounts = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone('America/Sao_Paulo')))





