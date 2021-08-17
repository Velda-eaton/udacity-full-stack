from flask import Flask, render_template, abort, request, Response, jsonify, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    website =  db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False )
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show',backref='Venues', lazy='joined', cascade="all, delete")
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.phone} {self.seeking_talent} {self.seeking_description} {self.genres}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website =  db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False )
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show',backref='Artist', lazy='joined', cascade="all, delete")
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.seeking_venue} {self.seeking_description} {self.genres}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))

    def __repr__(self):
      return f'<Show {self.id} {self.start_time} {self.venue_id} {self.artist_id}>'
