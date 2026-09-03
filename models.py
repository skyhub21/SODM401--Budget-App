from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    UserId = db.Column(db.String(30), primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    MicrosoftId = db.Column(db.String(100), unique=True, nullable=False)
    ResidentialAddress = db.Column(db.Text, nullable=True)
    ProfilePic = db.Column(db.String(255), nullable=True)
    CellphoneNumber = db.Column(db.String(20), nullable=True)
    CreatedOn = db.Column(db.DateTime(timezone=True), server_default=func.now())
    LastLogin = db.Column(db.DateTime(timezone=True), server_default=func.now())