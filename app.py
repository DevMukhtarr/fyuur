#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import click
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import distinct
from sqlalchemy.orm import load_only
import sys 
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
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(720))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(720))
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
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

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

  try:
      all_venues_location = db.session.query(distinct(Venue.city), Venue.state).all()

      for single_venue_location in all_venues_location:
        city = single_venue_location[0]
        state = single_venue_location[1]

        complete_data = {"city": city, "state": state, "venues": []}
        venues = Venue.query.filter_by(city=city, state=state).all()

        for venue in venues:
          id_of_venue = venue.id
          name_of_venue = venue.name

          upcoming_shows = (Show.query.filter_by(venue_id=id_of_venue).filter(Show.start_time > datetime.now()).all())
          venues_data = {"id": id_of_venue, "name":name_of_venue,"upcoming_shows":upcoming_shows}

          complete_data["venues"].append(venues_data)
          data.append(complete_data)
  except:
      db.session.rollback()
      return render_template("pages/home.html")
  finally:
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
      search_query = request.form.get("search_term")

      response = {"count": 0, "data": []}

      fields = ["id", "name"]
      all_venue_search_results = (db.session.query(Venue).filter
          (Venue.name.ilike(f"%{search_query}%") 
          | Venue.city.ilike(f"%{search_query}%") 
          | Venue.state.ilike(f"%{search_query}%")) 
        .options(load_only(*fields)).all())
      response["count"] = len(all_venue_search_results)
      for result in all_venue_search_results:
        data = {
            "id": result.id,
            "name": result.name
        }
        response["data"].append(data)

      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
      venue_clicked = Venue.query.get(venue_id)

      shows = Show.query.filter_by(venue_id=venue_id) ##error in here
      
      past_shows = []
      past_shows_from_db = shows.filter(Show.start_time < datetime.now()).all()
      for show in past_shows_from_db:
          artist = Artist.query.get(show.artist_id)
          show_data = {
              "artist_id": artist.id, 
              "artist_name": artist.name, 
              "artist_image_link": artist.image_link, 
              "start_time": str(show.start_time),
              }
          past_shows.append(show_data)

      upcoming_shows_from_db = shows.filter(Show.start_time >= datetime.now()).all()
      upcoming_shows = []
      for show in upcoming_shows_from_db:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
        }
        upcoming_shows.append(show_data)
      data = {
        "id": venue_clicked.id,
        "name": venue_clicked.name,
        "genres": venue_clicked.genres,
        "address": venue_clicked.address,
        "city": venue_clicked.city,
        "state": venue_clicked.state,
        "phone": venue_clicked.phone,
        "image_link": venue_clicked.image_link,
        "website": venue_clicked.website_link,
        "facebook_link": venue_clicked.facebook_link,
        "seeking_talent": venue_clicked.seeking_talent,
        "past_shows": past_shows,  
        "upcoming_shows": upcoming_shows, 
        "past_shows_count": len(past_shows), 
        "upcoming_shows_count": len(upcoming_shows), 
      }
  except:
    print(sys.exc_info())
    flash("Something went wrong. Please try again.")
  finally:
    db.session.close()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
        form = VenueForm()
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = form.genres.data
        facebook_link = form.facebook_link.data
        website_link = form.website_link.data
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data

        new_venue = Venue(
          name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres,facebook_link=facebook_link,website_link=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
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
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_query = request.form.get("search_term")
  response = {"count": 0, "data": []}

  fields = ["id", "name"]
  all_venue_search_results = (db.session.query(Artist).filter
      (Artist.name.ilike(f"%{search_query}%") 
      | Artist.city.ilike(f"%{search_query}%") 
      | Artist.state.ilike(f"%{search_query}%")) 
    .options(load_only(*fields)).all())
  response["count"] = len(all_venue_search_results)
  for result in all_venue_search_results:
    data = {
        "id": result.id,
        "name": result.name
    }
    response["data"].append(data)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
      artist_clicked = Artist.query.get(artist_id)
      shows = Show.query.filter_by(artist_id=artist_id)
      
      past_shows = []
      past_shows_from_db = shows.filter(Show.start_time < datetime.now()).all()
      for show in past_shows_from_db:
          venue = Venue.query.get(show.venue_id)
          show_data = {
              "venue_id": venue.id, 
              "venue_name": venue.name, 
              "venue_image_link": venue.image_link, 
              "start_time": str(show.start_time),
          }
          past_shows.append(show_data)
      #contains past show loop
      upcoming_shows = []
      upcoming_shows_from_db = shows.filter(Show.start_time >= datetime.now()).all()
      for show in upcoming_shows_from_db:
        venue = Venue.query.get(show.venue_id)
        show_data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time),
        }
        upcoming_shows.append(show_data)
      #contains upcoming show loop
      data = {
        "id": artist_clicked.id,
        "name": artist_clicked.name,
        "genres": artist_clicked.genres,
        "city": artist_clicked.city,
        "state": artist_clicked.state,
        "phone": artist_clicked.phone,
        "website": artist_clicked.website_link,
        "facebook_link": artist_clicked.facebook_link,
        "seeking_venue": artist_clicked.seeking_venue,
        "seeking_description": artist_clicked.seeking_description,
        "image_link": artist_clicked.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
  except:
    print(sys.exc_info())
    flash("Something went wrong..please retry")
  finally:
        db.session.close()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  try:
      form = ArtistForm()
      artist = Artist.query.get(artist_id)
      form.name.data = artist.name
      form.genres.data = artist.genres
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = artist.phone
      form.website_link.data = artist.website_link
      form.facebook_link.data = artist.facebook_link
      form.seeking_venue.data = artist.seeking_venue
      form.image_link.data = artist.image_link
      form.seeking_description.data = artist.seeking_description
  except:
    flash("Something went wrong. Please try again.")
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
      form = ArtistForm()
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      website_link = form.website_link.data
      facebook_link = form.facebook_link.data
      seeking_venue = form.seeking_venue.data
      image_link = form.image_link.data
      seeking_description = form.seeking_description.data



      new_artist_data = Artist.query.get(artist_id)

      new_artist_data.name = name
      new_artist_data.city = city
      new_artist_data.state = state
      new_artist_data.phone = phone
      new_artist_data.genres= genres
      new_artist_data.website_link = website_link
      new_artist_data.facebook_link = facebook_link
      new_artist_data.seeking_venue = seeking_venue
      new_artist_data.image_link = image_link
      new_artist_data.seeking_description = seeking_description

      db.session.add(new_artist_data)
      db.session.commit()

      db.session.refresh(new_artist_data)
      flash("The Artist "+ request.form['name'] +" Was Updated successfully")
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  try:
      form = VenueForm()
      venue = Venue.query.get(venue_id)
      form.name.data = venue.name
      form.genres.data = venue.genres
      form.address.data = venue.address
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.website_link.data = venue.website_link
      form.facebook_link.data = venue.facebook_link
      form.seeking_talent.data = venue.seeking_talent
      form.image_link.data = venue.image_link
      form.seeking_description.data = venue.seeking_description
  except:
    print(sys.exc_info())
    flash("Something went wrong. Please try again.")
  finally:
    db.session.close()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
      form = VenueForm()
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      genres = form.genres.data
      website_link = form.website_link.data
      facebook_link = form.facebook_link.data
      seeking_talent = form.seeking_talent.data
      image_link = form.image_link.data
      seeking_description = form.seeking_description.data



      new_venue_data = Venue.query.get(venue_id)

      new_venue_data.name = name
      new_venue_data.city = city
      new_venue_data.state = state
      new_venue_data.address = address
      new_venue_data.phone = phone
      new_venue_data.genres= genres
      new_venue_data.website_link = website_link
      new_venue_data.facebook_link = facebook_link
      new_venue_data.seeking_talent = seeking_talent
      new_venue_data.image_link = image_link
      new_venue_data.seeking_description = seeking_description

      db.session.add(new_venue_data)
      db.session.commit()

      db.session.refresh(new_venue_data)
  except:
    db.session.rollback()
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      form = ArtistForm()
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      facebook_link = form.facebook_link.data
      image_link = form.image_link.data
      website_link = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data

      new_artist = Artist(
        name= name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,website_link=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description 
      )
      db.session.add(new_artist)
      db.session.commit()
  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      db.session.rollback()
      flash('An error occurred '+ request.form['name'] +'Artist could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  try:
      data = []
      shows_data = Show.query.all()
      for show in shows_data:
        venue_id = show.venue_id
        artist_id = show.artist_id
        artist = Artist.query.get(artist_id)

        individual_show_data = {
        "venue_id": venue_id,
        "venue_name": Venue.query.get(venue_id).name,
        "artist_id": artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
        }
        data.append(individual_show_data)
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    # request.form['name']
    artist_found = Artist.query.get(artist_id)
    venue_found = Artist.query.get(venue_id)

    if artist_found is not None and venue_found is not None:
      new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(new_show)
      db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    flash("An error occured, show was not created")
  finally:
    db.session.close()
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
