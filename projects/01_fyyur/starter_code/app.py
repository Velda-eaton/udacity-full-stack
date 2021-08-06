#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import session
from forms import *
import string
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    shows = db.relationship('Show',backref=db.backref('Venues', cascade='all, delete'), lazy=True)
    
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
    shows = db.relationship('Show',backref=db.backref('Artist', cascade='all, delete'), lazy=True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.seeking_venue} {self.seeking_description} {self.genres}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
class StateVenues:
  def __init__(self, city, state):
    self.city = city
    self.state = state
    self.venues = []

@app.route('/venues')
def venues():
  data = []
  grouping = {}   
  for venue in Venue.query.order_by('name'):
    groupName = venue.city + venue.state 
    shows = Show.query.filter_by(venue_id=venue.id)
    venueDetails = {
      "id": venue.id, 
      "name": venue.name,
      "num_upcoming_shows":shows.count()} 
    if groupName not in grouping:
        grouping[groupName] = StateVenues(venue.city, venue.state)
    grouping[groupName].venues.append(venueDetails)
  
  for groupName in grouping:
      data.append({
        "city": grouping[groupName].city,
        "state": grouping[groupName].state,
        "venues": grouping[groupName].venues})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchStr = request.form['search_term'] 
  data = []
  for venue in Venue.query.filter(Venue.name.ilike('%'+searchStr+'%')).order_by('name'):
    shows = Show.query.filter_by(venue_id=venue.id)
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows":shows.count()})
  
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  isDuplicate = True
  errMessage = ""

  try:
    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    address = request.form["address"]
    phone = request.form["phone"].translate(str.maketrans('','',string.punctuation))
    image_link = request.form["image_link"]
    website =  request.form["website_link"]
    facebook_link = request.form["facebook_link"]
    genres = request.form.getlist("genres")
    print(genres)
    if "seeking_talent" in request.form:      
      seeking_talent = True
      seeking_description = request.form["seeking_description"]
    else:
      seeking_talent = False
      seeking_description = ""

    # Validate the entries
    # I'm presuming that the venue name, website and fb pages, if enetered,  must be unique.
    isDuplicate=bool(Venue.query.filter_by(name=name).first())
    if isDuplicate == True:
      errMessage += " The venue is already in the database."
    
    if website != '' and isDuplicate == False:
      isDuplicate=bool(Venue.query.filter_by(website=website).first())
      if isDuplicate == True:
        errMessage += " The website is already in the database."
    
    if facebook_link != '' and isDuplicate == False:
      isDuplicate=bool(Venue.query.filter_by(facebook_link=facebook_link).first())
      if isDuplicate == True:
        errMessage += " The facebook link is already in the database."

    validPhone = True
    if len(phone) != 10 or phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."

    if isDuplicate == False and validPhone:
      venue = Venue(
        name = name,
        city = city,
        state = state,
        address = address,
        phone = phone,
        image_link = image_link,
        website =  website,
        facebook_link = facebook_link,
        genres = genres,
        seeking_talent = seeking_talent,
        seeking_description = seeking_description)
      db.session.add(venue)
      db.session.commit()
      newVenue = Venue.query.filter_by(name=name).first()
    else:
      # TODO: Nice to have, make the error message appear on the screen instead of redirecting
      error=True
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
    flash('An error occurred. Venue ' + name + ' could not be listed.' + errMessage)
  else:
    flash('Venue ' + name + ' was successfully listed! ID:' + str(newVenue.id))
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  for artist in Artist.query.order_by('name'):
    data.append({"id": artist.id,"name": artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searchStr = request.form['search_term'] 
  data = []
  for artist in Artist.query.filter(Artist.name.ilike('%'+searchStr+'%')).order_by('name'):
    data.append({"id": artist.id,"name": artist.name})
  
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  pastShows = []
  upcomingShows = []
  artist = Artist.query.get(artist_id)
  print(artist)
  print(Show.query.join(Venue))
  print(Show.query.filter_by(artist_id=artist_id).join(Venue).all())
  for show in Show.query.filter_by(artist_id=artist_id).join(Venue).all():
    venue = Venue.query.get(show.venue_id)
    showDetails = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
    if show.start_time>datetime.now():      
      upcomingShows.append(showDetails)
      print ("future")
    else:
      pastShows.append(showDetails)
      print ("past")
  print(pastShows)
  print(upcomingShows)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
  print(data)
  # velda this is where you are need to add data to venue and shows before I can test join 
  # TODO: replace with real artist data from the artist table, using artist_id
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  isDuplicate = True
  errMessage = ""
  try:
    name = request.form["name"]
    genres = request.form.getlist("genres")
    city = request.form["city"]
    state = request.form["state"]
    phone = request.form["phone"].translate(str.maketrans('','',string.punctuation))
    website =  request.form["website_link"]
    facebook_link = request.form["facebook_link"]
    image_link = request.form["image_link"]
    if "seeking_venue" in request.form:      
      seeking_venue = True
      seeking_description = request.form["seeking_description"]
    else:
      seeking_venue = False
      seeking_description = ""

    # Validate the entries
    # I'm presuming that the artist name, website and fb pages, if enetered,  must be unique.
    isDuplicate=bool(Artist.query.filter_by(name=name).first())
    if isDuplicate == True:
      errMessage += " The artist is already in the database."
    
    if website != '' and isDuplicate == False:
      isDuplicate=bool(Artist.query.filter_by(website=website).first())
      if isDuplicate == True:
        errMessage += " The website is already in the database."

    if facebook_link != '' and isDuplicate == False:
      isDuplicate=bool(Artist.query.filter_by(facebook_link=facebook_link).first())
      if isDuplicate == True:
        errMessage += " The facebook link is already in the database."

    validPhone = True
    if len(phone) != 10 or phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."

    if isDuplicate == False and validPhone:
      artist = Artist(
        name = name,
        genres = genres,
        city = city,
        state = state,
        phone = phone,
        image_link = image_link,
        website =  website,
        facebook_link = facebook_link,
        seeking_venue = seeking_venue,
        seeking_description = seeking_description)
      db.session.add(artist)
      db.session.commit()

      newArtist = Artist.query.filter_by(name=name).first()
    else:
      # TODO: Nice to have, make the error message appear on the screen instead of redirecting
      error=True
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  # on successful db insert, flash success
  if error:
    flash('An error occurred. Artist ' + name + ' could not be listed.' + errMessage)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed! ID:' + str(newArtist.id))

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  print(request.form)
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  isDuplicate = True
  errMessage = ""
  try:
    venue_id = request.form["venue_id"]
    artist_id = request.form["artist_id"]
    start_time = datetime.strptime(request.form["start_time"], '%Y-%m-%d %H:%M:%S')

    # Validate that this is not a duplicate
    isDuplicate=bool(Show.query.filter_by(venue_id=venue_id,artist_id = artist_id,start_time = start_time).first())
    if isDuplicate == True:
      errMessage += " The show is already in the database."

    if isDuplicate == False:
      show = Show(
        venue_id = venue_id,
        artist_id = artist_id,
        start_time = start_time)
      db.session.add(show)
      db.session.commit()
    else:
      error=True
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  # on successful db insert, flash success
  if error:
    flash('An error occurred. Show could not be listed.' + errMessage)
  else:
    flash('Show was successfully listed!')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
