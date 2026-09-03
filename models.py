from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "User"
    UserId = db.Column(db.String(30), primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), unique=True, nullable = False)
    UserRole = db.Column(db.String(20), nullable = False) #Student/Tutor/Mentor
    AvgRating = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    IsVerified = db.Column(db.Boolean, default=False)
    MicrosoftId = db.Column(db.String(50), unique=True,nullable=False)
    CreatedOn = db.Column(db.DateTime(timezone=True), server_default= func.now())
    LastLogin = db.Column(db.DateTime(timezone=True), server_default= func.now())