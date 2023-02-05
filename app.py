from sqlalchemy import text

class User_Model(db.Model):
    #use server_default if table already created to add default value
    setting = db.Column(db.Boolean, nullable=False, server_default=text('1'))