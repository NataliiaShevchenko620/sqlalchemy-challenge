from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# Reflect the database tables to the classes
Base.prepare(engine, reflect=True)

# Create two classes based on the reflection results
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""

    # Custom logging
    print("Server received request for 'Home' page...")

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - precipitation for the last 12 months of data<br/>"
        f"/api/v1.0/stations - list of available stations<br/>"
        f"/api/v1.0/tobs- the dates and temperature observations of the most-active station for the the last 12 months of data<br/>"
        f"/api/v1.0/YYYY-MM-DD - the minimum temperature, the average temperature, and the maximum temperature for all the dates greater than or equal to the start date<br/> "
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD - the minimum temperature, the average temperature, and the maximum temperature for the dates from the start date to the end date, inclusive"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Custom logging
    print("Server received request for precipitation for the last 12 months of data...")

    # Creating a session to the database
    session = Session(engine)

    # Starting from the most recent data point in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set
    one_year_ago = datetime.strptime(most_recent_date[0], '%Y-%m-%d') - timedelta(days=366)
    
    # Perform a query to retrieve the date and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Closing the session to the database
    session.close()
    
    # Save the query results as a dictionary with date as a key and precipitation is a value
    prcp_dict = [{date: prcp for date, prcp in prcp_data}]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Custom logging
    print("Server received request for a list of available stations...")

    # Creating a session to the database
    session = Session(engine)

    # Perform a query to retrieve all station names in the database
    stations_data = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .all()

    # Closing the session to the database
    session.close()

    # Save the query results as a dictionary with station as a key and count of measurements is a value
    stations_dict = [{station: count for station, count in stations_data}]

    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Custom logging
    print("Server received request for the dates and temperature observations of the most-active station for the previous year of data...")

    # Creating a session to the database
    session = Session(engine)

    # Perform a query to find the most active stations (i.e. which stations have the most rows?)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]
    
    # Starting from the most recent data point in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set
    one_year_ago = datetime.strptime(most_recent_date[0], '%Y-%m-%d') - timedelta(days=366)

    # Perform a query to retrieve the date and temperature observations for one year of data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Closing the session to the database
    session.close()

    # Save the query results as a dictionary with date as a key and temperature observation is a value
    tobs_dict = [{date: tobs for date, tobs in tobs_data}]

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Custom logging
    print("Server received request for the minimum temperature, the average temperature, and the maximum temperature for all the dates greater than or equal to the start date...")

    # Creating a session to the database
    session = Session(engine)

    # Covert the <start> parameter from a string to datetime using '%Y-%m-%d' format (assuming YYYY-MM-DD input format)
    start_date = datetime.strptime(start, '%Y-%m-%d')

    # Define a list of columns to extract and applied aggregation functions
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Perform the query to retrieve min, average and max temperature observations for the dates greater or equal to the start date
    # *sel here means "extration" of all items from the sel list as comma separated parameters
    # i.e. query(*sel) is equal to query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    results = session.query(*sel).filter(Measurement.date >= start_date).all()

    # Closing the session to the database
    session.close()
    #temps = list(np.ravel(results))
    #temp_dict = {'TMIN': temps[0], 'TAVG': temps[1], 'TMAX': temps[2]}

    # Save the query result as a dictionary
    temp_dict = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Custom logging
    print("Server received request for the minimum temperature, the average temperature, and the maximum temperature for the dates from the start date to the end date, inclusive...")

    # Creating a session to the database
    session = Session(engine)

    # Covert the <start> parameter from a string to datetime using '%Y-%m-%d' format (assuming YYYY-MM-DD input format)
    start_date = datetime.strptime(start, '%Y-%m-%d')

    # Covert the <end> parameter from a string to datetime using '%Y-%m-%d' format (assuming YYYY-MM-DD input format)
    end_date = datetime.strptime(end, '%Y-%m-%d')

    # Define a list of columns to extract and applied aggregation functions
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Perform the query to retrieve min, average and max temperature observations for the dates between start and end dates inclusively
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Closing the session to the database
    session.close()

    #temps = list(np.ravel(results))
    #temp_dict = {'TMIN': temps[0], 'TAVG': temps[1], 'TMAX': temps[2]}

    # Save the query result as a dictionary
    temp_dict = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}
    
    return jsonify(temp_dict)

# Run API in the debug mode
if __name__ == '__main__':
    app.run(debug=True)

