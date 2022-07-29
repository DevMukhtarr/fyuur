#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from unicodedata import name
from urllib import response
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
from sqlalchemy import distinct, true
from sqlalchemy.orm import load_only
import sys 
from sqlalchemy.sql import text
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database


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
  venues = Venue.query.all()
  data = []

  name_dict = set()
  for venue in venues:
    name_dict.add((venue.city, venue.state))
  for x in name_dict:
    new_dict = {
      "city": x[0],
      "state": x[1],
      "venues": []
    }
    data.append(new_dict)
  for venue in venues:
    for venue_list in data:
      if venue_list['city'] == venue.city:
        venues_complete_data = {
          "id": venue.id,
          "name": venue.name,
        }
        venue_list["venues"].append(venues_complete_data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  response = {}
  venues = Venue.query.all()
  found_list = []
  toadd = []
  for venue in venues:
    if search_term in venue.name.lower():
      found_list.append(venue.name)
      response["count"] = len(found_list)
      for found in found_list:
        single_toadd = {
          "id": venue.id,
          "name": found
        }
      toadd.append(single_toadd)
  response["data"] = toadd

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
      venue_clicked = Venue.query.get(venue_id)
      shows = Show.query.all()
      data = {}
      data["id"] = venue_clicked.id
      data["name"] = venue_clicked.name
      data["genres"] = venue_clicked.genres
      data["address"] = venue_clicked.address
      data["city"] = venue_clicked.city
      data["phone"] = venue_clicked.phone
      data["website"] = venue_clicked.website_link
      data["facebook_link"] = venue_clicked.facebook_link
      data["seeking_talent"] = venue_clicked.seeking_talent
      data["seeking_description"] = venue_clicked.seeking_description
      data["image_link"] = venue_clicked.image_link
      data["past_shows"] = []
      data["upcoming_shows"] = []

      # past show quey
      past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
      # upcoming show query
      upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
      for show in upcoming_shows_query:
        upcoming_shows = {
            "venue_id": show.artist_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "start_time": str(show.start_time)
          }
        data["upcoming_shows"].append(upcoming_shows)
        data["upcoming_shows_count"] = len(data["upcoming_shows"])
      for show in past_shows_query:
        past_shows = {
            "venue_id": show.artist_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "start_time": str(show.start_time)
          }
        data["past_shows"].append(past_shows)
        data["past_shows_count"] = len(data["past_shows"])
          
  except:
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
    form = VenueForm()
    try:
      new_venue = Venue(
      name=  form.name.data,
      city= form.city.data,
      state= form.state.data,
      address= form.address.data,
      phone= form.phone.data,
      genres= form.genres.data,
      image_link= form.image_link.data,
      facebook_link= form.facebook_link.data,
      website_link= form.website_link.data,
      seeking_talent= form.seeking_talent.data,
      seeking_description=form.seeking_description.data
      )
      flash('Venue was successfully listed')
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
    except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      db.session.rollback()
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
  search_term = request.form.get('search_term')
  response = {}
  artists = Artist.query.all()
  found_list = []
  toadd = []
  for artist in artists:
    if search_term in artist.name.lower():
      found_list.append(artist.name)
      response["count"] = len(found_list)
      for found in found_list:
        single_toadd = {
          "id": artist.id,
          "name": found,
          "num_upcoming_shows": 0
        }
      toadd.append(single_toadd)
  response["data"] = toadd

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
      artist_clicked = Artist.query.get(artist_id)
      shows = Show.query.all()
      data = {}
      data["id"] = artist_clicked.id
      data["name"] = artist_clicked.name
      data["genres"] = artist_clicked.genres
      data["state"] = artist_clicked.state
      data["city"] = artist_clicked.city
      data["phone"] = artist_clicked.phone
      data["website"] = artist_clicked.website_link
      data["facebook_link"] = artist_clicked.facebook_link
      data["seeking_venue"] = artist_clicked.seeking_venue
      data["seeking_description"] = artist_clicked.seeking_description
      data["image_link"] = artist_clicked.image_link
      data["past_shows"] = []
      data["upcoming_shows"] = []

      past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
      upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
      for show in upcoming_shows_query:
        upcoming_shows = {
            "venue_id": show.artist_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "venue_image_link": Venue.query.get(show.venue_id).image_link,
            "start_time": str(show.start_time)
          }
        data["upcoming_shows"].append(upcoming_shows)
        data["upcoming_shows_count"] = len(data["upcoming_shows"])
      for show in past_shows_query:
        past_shows = {
            "venue_id": show.artist_id,
            "venue_name": Venue.query.get(show.venue_id).name,
            "venue_image_link": Venue.query.get(show.venue_id).image_link,
            "start_time": str(show.start_time)
          }
        data["past_shows"].append(past_shows)
        data["past_shows_count"] = len(data["past_shows"])
  except:
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
  form = ArtistForm()
  try:
    new_artist = Artist(
        name=  form.name.data,
        city= form.city.data,
        state= form.state.data,
        phone= form.phone.data,
        genres= form.genres.data,
        image_link= form.image_link.data,
        facebook_link= form.facebook_link.data,
        website_link= form.website_link.data,
        seeking_venue= form.seeking_venue.data,
        seeking_description=form.seeking_description.data
        )
    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist was successfully listed')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      db.session.rollback()
      flash('An error occurred '+ request.form['name'] +' Artist could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  try:
      data = []
      for show in shows:
        single_show = {
          "venue_id": show.venue_id,
          "venue_name": Venue.query.get(show.venue_id).name,
          "artist_id": show.artist_id,
          "artist_name": Artist.query.get(show.artist_id).name,
          "artist_image_link": Artist.query.get(show.artist_id).image_link,
          "start_time": str(show.start_time)
        }
        data.append(single_show)
  except:
      db.session.rollback()
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
    artist_found = Artist.query.get(artist_id)
    venue_found = Artist.query.get(venue_id)

    new_show = Show(
    artist_id=artist_id, 
    venue_id=venue_id, 
    start_time=start_time
    )
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
