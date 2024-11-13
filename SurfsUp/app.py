# Import the dependencies.
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"   
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     # Starting from the most recent data point in the database. 
     most_recent_date = session.query(func.max(measurement.date)).scalar()

     # Calculate the date one year from the last date in data set.
     one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
     one_year_ago = one_year_ago.strftime('%Y-%m-%d')

     # Query the last year of precipitation data
     last_year = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).\
        order_by(measurement.date).all()
     
     # Create a dictionary from the query results
     precipitation_data = {date: prcp for date, prcp in last_year}

     return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(station.station, station.name).all()

    # Create a list of dictionaries from the query results
    stations_list = [{"station": station, "name": name} for station, name in results]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Starting from the most recent data point in the database. 
    most_recent_date = session.query(func.max(measurement.date)).scalar()

    # Calculate the date one year from the last date in data set.
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')

    # Query the last year of temperature observations for the most active station
    last_year_tobs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= one_year_ago).\
        order_by(measurement.date).all()

    # Create a list of dictionaries from the query results
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in last_year_tobs]

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start):
    # Query the min, max, and average temperatures from the start date to the end of the dataset
    results = session.query(
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)
    ).filter(measurement.date >= start).all()

    # Unpack the results
    min_temp, max_temp, avg_temp = results[0]

    # Create a dictionary to hold the results
    temperature_data = {
        "Start Date": start,
        "Min Temperature": min_temp,
        "Max Temperature": max_temp,
        "Avg Temperature": avg_temp
    }

    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Query the min, max, and average temperatures from the start date to the end date
    results = session.query(
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)
    ).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Unpack the results
    min_temp, max_temp, avg_temp = results[0]

    # Create a dictionary to hold the results
    temperature_data = {
        "Start Date": start,
        "End Date": end,
        "Min Temperature": min_temp,
        "Max Temperature": max_temp,
        "Avg Temperature": avg_temp
    }

    return jsonify(temperature_data)