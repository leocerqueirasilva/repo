
from apps import db
from flask import Flask



class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    setting = db.Column(db.String(1020))


    

    

    def to_dict(self):
        return {'username': self.username}




