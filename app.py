from flask import Flask, jsonify
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/> "
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
        
    )

@app.route("/api/v1.0/precipitation")
def precip():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    lastDayOfData = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()[0][0]
    oneYearAgo = dt.datetime.strptime(lastDayOfData, '%Y-%m-%d')-dt.timedelta(days=366)
    dateQuery = dt.datetime.strftime(oneYearAgo,'%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    last12pcpn = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date > dateQuery).all()

    session.close()

    all_obs = []

    for date, pcpn in last12pcpn:
        ob_dict = {}
        ob_dict['date'] = date
        ob_dict['precip'] = pcpn
        all_obs.append(ob_dict)

    return jsonify(all_obs)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    stationList = session.query(Station.station,Station.name).all()

    session.close()

    all_stations = []

    for id, name in stationList:

        stationDict = {}
        stationDict['id'] = id
        stationDict['name'] = name
        all_stations.append(stationDict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temps():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    lastDayOfData = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()[0][0]
    oneYearAgo = dt.datetime.strptime(lastDayOfData, '%Y-%m-%d')-dt.timedelta(days=366)
    dateQuery = dt.datetime.strftime(oneYearAgo,'%Y-%m-%d')

    # Grab the temp obs over the last year
    tempObs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date > dateQuery).all()

    session.close()

    all_tobs = []

    for date,temp in tempObs:

        tempDict = {}
        tempDict['date'] = date
        tempDict['temp'] = temp
        all_tobs.append(tempDict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def tempCalc(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    tempStats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    session.close()

    statDict = {}
    statDict['min'] = tempStats[0][0]
    statDict['max'] = tempStats[0][1]
    statDict['avg'] = tempStats[0][2]

    return jsonify(statDict)

@app.route("/api/v1.0/<start>/<end>")
def tempCalcRange(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    tempStats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    statDict = {}
    statDict['min'] = tempStats[0][0]
    statDict['max'] = tempStats[0][1]
    statDict['avg'] = tempStats[0][2]

    return jsonify(statDict)


# Run the app if called as the main program
if __name__ == "__main__":
    app.run(debug=True)