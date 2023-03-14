# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import UserMixin

from database import db

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    email = db.Column(db.Unicode, nullable = False)
    password = db.Column(db.Unicode, nullable = False)
    active = db.Column(db.Integer)
    @hybrid_property
    def roles(self):
        return []
    @roles.setter
    def roles(self, role):
        pass
    
    # def is_authenticated(self):
    #     return True

    # def is_active(self):   
    #     return True           

    # def is_anonymous(self):
    #     return False          

    # def get_id(self):         
    #     return (self.id)
    
    trackers = db.relationship("Tracker")
    logs = db.relationship("Log")

class Tracker(db.Model):
    __tablename__ = "tracker"
    tracker_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    tracker_name = db.Column(db.Unicode, nullable = False)
    description = db.Column(db.Unicode)
    tracker_type = db.Column(db.Integer, nullable = False)
    logs = db.relationship("Log", cascade='all, delete-orphan', backref='tracker')
    settings = db.relationship("Setting", cascade='all, delete-orphan', backref='tracker')
    last_review = db.Column(db.DateTime, default = db.func.now())
    last_value = db.Column(db.Integer, nullable = False)
    
            
class Log(db.Model):
    __tablename__ = "log"
    log_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable = False)
    value = db.Column(db.Integer, nullable = False)
    desc = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default = db.func.now())
    
class Setting(db.Model):
    __tablename__ = "setting"
    setting_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    setting_name = db.Column(db.Unicode, nullable = False)
    setting_value = db.Column(db.Integer, nullable = False)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable = False)
    
class Type(db.Model):
    __tablename__ = "type"
    tracker_type_int = db.Column(db.Integer, nullable = False, primary_key = True)
    tracker_type_name = db.Column(db.String, nullable = False)
    
class Role(db.Model):
    __tablename__ = "role"
    role_id = db.Column(db.Integer, nullable = False, primary_key = True)