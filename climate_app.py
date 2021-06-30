# Dependencies

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template

# Use SQLAlchemy "create_engine" to connect to your sqlite database.
# Use SQLAlchemy "automap_base()" to reflect your tables into classes and save a reference to those classes called "Station" and "Measurement".
# Link Python to the database by creating an SQLAlchemy session.

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station

# Start by finding the most recent date in the data set.
# Using this date, retrieve the last 12 months of precipitation data by querying the 12 preceding months of data.

latest_date = dt.date(2017, 8, 23)
last12months = latest_date - dt.timedelta(days=365)

Station = Base.classes.station
Measurement = Base.classes.measurement

session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)
app = Flask(__name__)

# List all available api routes.
@app.route("/")
def index():
    return (
        f"Routes:<br />"
        f"<br />"
        f"/api/v1.0/precipitation<br />"
        f"/api/v1.0/stations<br />"
        f"/api/v1.0/tobs<br />"
        f"/api/v1.0/temp/start/end<br />"
        f"/api/v1.0/<start><br />"
        f"/api/v1.0/<start>/<end><br />"
        "<h1><center>WELCOME TO SURF'S UP!</center></h1><br/>"
        "<h2><center>Please plug in the browser any of the available routes:</h2></center><br/>"
        "<h3><center>/api/v1.0/precipitation</h3></center><br/>"
        "<h3><center>/api/v1.0/stations</h3></center><br/>"
        "<h3><center>/api/v1.0/tobs</h3></center><br/>"
        "<h3><center>/api/v1.0/<start></h3></center>"
        "<center>Note: Type the start date in the form of %mm-%dd</center>"
        "<h3><center>/api/v1.0/<start>/<end></h3></center>"
        "<center>Note: API request takes two parameters: Start date / End date</center>"
        "<center>Type dates in the form of %yyyy-%mm-%dd</center>"
        "<br/>"
    )

# Convert the query results to a Dictionary using "date" as the key and "prcp" as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precip():
    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_from_last).all()
    precip = {}
    for result in prcp_query:
        prcp_list = {result.date: result.prcp, "prcp": result.prcp}
        precip.update(prcp_list)

    return jsonify(precip)

# Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def station():
    stations_list = session.query(Station.station).all()
    stations = list(np.ravel(stations_list))
    return jsonify(stations)

# Query for the dates and temperature observations from a year from the last data point.

# Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_from_last).all()
    tobs_list = list(np.ravel(tobs_query))
    return jsonify(tobs_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, TMIN, TAVG, and TMAX are calculated for all dates greater than and equal to the start date.

# When given the start and the end date, TMIN, TAVG, and TMAX are calculated for dates between the start and end date inclusive.

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    if end != "":
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).filter(Measurement.date.between(year_from_last, last_data_point)).all()
        t_stats = list(np.ravel(temp_stats))
        return jsonify(temp_stats)

    else:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
            func.max(Measurement.tobs)).filter(Measurement.date > last_data_point).all()
        t_stats = list(np.ravel(temp_stats))
        return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(port=9000, debug=True)