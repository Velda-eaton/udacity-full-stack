#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from models import *
import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import session
from forms import *
import string
import sys

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
    shows = venue.shows
    upcomingShows = 0
    for show in shows:
      if show.start_time>datetime.now():
        upcomingShows += 1
    venueDetails = {
      "id": venue.id, 
      "name": venue.name,
      "num_upcoming_shows":upcomingShows} 
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
  pastShows = []
  upcomingShows = []
  venue = Venue.query.get(venue_id)
  for show in Show.query.filter_by(venue_id=venue_id).join(Artist).all():
    artist = Artist.query.get(show.artist_id)
    showDetails = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
    if show.start_time>datetime.now():      
      upcomingShows.append(showDetails)
    else:
      pastShows.append(showDetails)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": '-'.join([venue.phone[:3], venue.phone[3:6], venue.phone[6:]]),
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
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
  isDuplicate = False
  errMessage = ""

  try:
    form = VenueForm()  
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data.translate(str.maketrans('','',string.punctuation)),
      image_link = form.image_link.data,
      website =  form.website_link.data,
      facebook_link = form.facebook_link.data,
      genres = request.form.getlist("genres"),
      seeking_talent = False,
      seeking_description = "")
      
    if "seeking_talent" in request.form:      
      venue.seeking_talent = True
      venue.seeking_description = form.seeking_description.data
      
    # Validate the entries
    # I'm presuming that the venue name, website and fb pages, if enetered,  must be unique.
    if bool(Venue.query.filter_by(name=venue.name).first()) == True:
      isDuplicate = True
      errMessage += " The venue is already in the database."
      
    if venue.website != '' and bool(Venue.query.filter_by(website=venue.website).first()) ==True:
      isDuplicate = True
      errMessage += " The website is already in the database."
        
    if venue.facebook_link != '' and bool(Venue.query.filter_by(facebook_link=venue.facebook_link).first()) == True:
      isDuplicate = True
      errMessage += " The facebook link is already in the database."
        
    validPhone = True
    if (len(venue.phone) != 0 and len(venue.phone) != 10) or venue.phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."      
      
    if isDuplicate == False and validPhone:
      db.session.add(venue)
      db.session.commit()
      newVenue = Venue.query.filter_by(name=venue.name).first()
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
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' + errMessage)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed! ID:' + str(newVenue.id))
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:        
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      abort(500)
  finally:   
      db.session.close()
  
  flash('Venue ' + venue.name + ' was successfully deleted! ')
  return  jsonify({ 'success': True })

#  Update Venues
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populate form with values from venue with ID <venue_id>
  venue = Venue.query.get_or_404(venue_id)
  venue.phone = '-'.join([venue.phone[:3], venue.phone[3:6], venue.phone[6:]])
  venue.website_link = venue.website
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  isDuplicate = False
  errMessage = ""

  try:
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm()
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.image_link = form.image_link.data
    venue.genres = request.form.getlist("genres")
      
    if "seeking_talent" in request.form:      
      venue.seeking_talent = True
      venue.seeking_description = form.seeking_description.data
    else:
      venue.seeking_talent = False
      venue.seeking_description = ""

    name = request.form["name"]
    phone = request.form["phone"].translate(str.maketrans('','',string.punctuation))
    website =  request.form["website_link"]
    facebook_link = request.form["facebook_link"]

    # Validate the entries
    # I'm presuming that the venue name, website and fb pages, if enetered,  must be unique.
    if venue.name != name:      
      if bool(Venue.query.filter_by(name=name).first()) == True:
        isDuplicate = True
        errMessage += " The venue is already in the database."        

    if venue.website != website and website != '':
        if bool(Venue.query.filter_by(website=website).first()) == True:
          isDuplicate = True
          errMessage += " The website is already in the database."
    
    if venue.facebook_link != facebook_link and facebook_link != '':
      if bool(Venue.query.filter_by(facebook_link=facebook_link).first()) == True:        
        isDuplicate = True
        errMessage += " The facebook link is already in the database."

    validPhone = True
    if venue.phone != phone and (len(phone) != 0 and len(phone) != 10) or phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."

    if isDuplicate == False and validPhone:
      venue.name = name
      venue.phone = phone
      venue.website = website
      venue.facebook_link = facebook_link
      db.session.commit()
    else:
      error=True
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.' + errMessage)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))


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
    else:
      pastShows.append(showDetails)
      
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": '-'.join([artist.phone[:3], artist.phone[3:6], artist.phone[6:]]),
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
  
  return render_template('pages/show_artist.html', artist=data)

#  Update Artists
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):  
  # populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get_or_404(artist_id)
  artist.phone = '-'.join([artist.phone[:3], artist.phone[3:6], artist.phone[6:]])
  artist.website_link = artist.website
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  isDuplicate = False
  errMessage = ""
  
  try:
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm() 
    artist.city = form.city.data
    artist.state = form.state.data
    artist.genres = request.form.getlist("genres")
    artist.image_link = form.image_link.data
    if "seeking_talent" in request.form:      
      artist.seeking_talent = True
      artist.seeking_description = form.seeking_description.data
    else:
      artist.seeking_talent = False
      artist.seeking_description = ""

    name = form.name.data
    phone = form.phone.data.translate(str.maketrans('','',string.punctuation))
    website =  form.website_link.data
    facebook_link = form.facebook_link.data

    # Validate the entries
    # I'm presuming that the venue name, website and fb pages, if enetered,  must be unique.
    if artist.name != name and bool(Venue.query.filter_by(name=name).first()) == True:
      isDuplicate = True
      errMessage += " The venue is already in the database."
    
    if artist.website != website and website != '' and  bool(Venue.query.filter_by(website=website).first()) == True:
      isDuplicate = True
      errMessage += " The website is already in the database."
    
    if artist.facebook_link != facebook_link and facebook_link != '' and bool(Venue.query.filter_by(facebook_link=facebook_link).first()) == True:
      isDuplicate = True
      errMessage += " The facebook link is already in the database."

    validPhone = True
    if artist.phone != phone and (len(phone) != 0 and len(phone) != 10) or phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."

    if isDuplicate == False and validPhone:
      artist.name = name
      artist.phone = phone
      artist.website = website
      artist.facebook_link = facebook_link
      db.session.commit()
    else:
      error=True
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.' + errMessage)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


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
  isDuplicate = False
  errMessage = ""
  try:    
    form = ArtistForm() 
    artist = Artist(
        name = form.name.data,
        genres = request.form.getlist("genres"),
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data.translate(str.maketrans('','',string.punctuation)),
        image_link = form.image_link.data,
        website =  form.website_link.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = False,
        seeking_description = "")

    if "seeking_venue" in request.form:      
      artist.seeking_venue = True
      artist.seeking_description = form.seeking_description.data

    # Validate the entries
    # I'm presuming that the artist name, website and fb pages, if enetered,  must be unique.
    if bool(Artist.query.filter_by(name=artist.name).first()) == True:
      isDuplicate = True
      errMessage += " The artist is already in the database."
    
    if artist.website != '' and bool(Artist.query.filter_by(website=artist.website).first()) == True:
      isDuplicate = True
      errMessage += " The website is already in the database."

    if artist.facebook_link != '' and bool(Artist.query.filter_by(facebook_link=artist.facebook_link).first()) == True:
      isDuplicate =True
      errMessage += " The facebook link is already in the database."

    validPhone = True
    if (len(artist.phone) != 0 and len(artist.phone) != 10) or artist.phone.isnumeric == False: 
      validPhone = False
      errMessage += " Invalid phone number."

    if isDuplicate == False and validPhone:      
      db.session.add(artist)
      db.session.commit()
      newArtist = Artist.query.filter_by(name=artist.name).first()
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
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.' + errMessage)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed! ID:' + str(newArtist.id))

  return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:        
      artist = Artist.query.get(artist_id)
      db.session.delete(artist)
      db.session.commit()
  except:
      db.session.rollback()
      abort(500)
  finally:   
      db.session.close()
  
  flash('Artist ' + artist.name + ' was successfully deleted! ')
  return  jsonify({ 'success': True })

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_query = db.session.query(Show, Venue, Artist)\
    .join(Venue, Venue.id == Show.venue_id)\
    .join(Artist, Artist.id == Show.artist_id)
  
  data = []
  for show in show_query.all():
    showDetails = {
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")}
    data.append(showDetails)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  isDuplicate = False
  errMessage = ""
  try:    
    form = ShowForm()
    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    start_time = datetime.strptime(form.start_time.data, '%Y-%m-%d %H:%M:%S')

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
