from flask import Flask, render_template, session, request, redirect, flash, url_for, jsonify, Response, logging
from interfaces import databaseinterface, camerainterface, soundinterface
import robot #robot is class that extends the brickpi class
import global_vars as GLOBALS #load global variables
import logging, time

#Creates the Flask Server Object
app = Flask(__name__); app.debug = True
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
GLOBALS.DATABASE = databaseinterface.DatabaseInterface('databases/RobotDatabase.db', app.logger)

#Log messages
def log(message):
    app.logger.info(message)
    return

#create a login page
@app.route('/', methods=['GET','POST'])
def login():
    if 'userid' in session:
        return redirect('/dashboard')
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        log(userdetails)
        if userdetails:
            user = userdetails[0] #get first row in results
            if user['password'] == request.form.get("password"):
                session['userid'] = user['userid']
                session['permission'] = user['permission']
                session['name'] = user['name']
                return redirect('/dashboard')
            else:
                message = "Login Unsuccessful"
        else:
            message = "Login Unsuccessful"
    return render_template('login.html', data = message)    

# Load the ROBOT
@app.route('/robotload', methods=['GET','POST'])
def robotload():
    sensordict = None
    if not GLOBALS.CAMERA:
        log("LOADING CAMERA")
        GLOBALS.CAMERA = camerainterface.CameraInterface()
        GLOBALS.CAMERA.start()
    if not GLOBALS.ROBOT: 
        log("LOADING THE ROBOT")
        GLOBALS.ROBOT = robot.Robot(20, app.logger)
        GLOBALS.ROBOT.configure_sensors() #defaults have been provided but you can 
        GLOBALS.ROBOT.reconfig_IMU()
    if not GLOBALS.SOUND:
        log("LOADING THE SOUND")
        GLOBALS.SOUND = soundinterface.SoundInterface()
        GLOBALS.SOUND.say("I am ready")
    sensordict = GLOBALS.ROBOT.get_all_sensors()
    return jsonify(sensordict)

# ---------------------------------------------------------------------------------------
# Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def robotdashboard():
    if not 'userid' in session:
        return redirect('/')
    enabled = int(GLOBALS.ROBOT != None)
    return render_template('dashboard.html', robot_enabled = enabled )

#Used for reconfiguring IMU
@app.route('/reconfig_IMU', methods=['GET','POST'])
def reconfig_IMU():
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.reconfig_IMU()
        sensorconfig = GLOBALS.ROBOT.get_all_sensors()
        return jsonify(sensorconfig)
    return jsonify({'message':'ROBOT not loaded'})

#calibrates the compass but takes about 10 seconds, rotate in a small 360 degrees rotation
@app.route('/compass', methods=['GET','POST'])
def compass():
    data = {}
    if GLOBALS.ROBOT:
        data['message'] = GLOBALS.ROBOT.calibrate_imu(10)
    return jsonify(data)

@app.route('/sensors', methods=['GET','POST'])
def sensors():
    data = {}
    if GLOBALS.ROBOT:
        data = GLOBALS.ROBOT.get_all_sensors()
    return jsonify(data)

# YOUR FLASK CODE------------------------------------------------------------------------
@app.route('/missions', methods = ['GET', 'POST'])
def missions():
    if request.method == 'POST':
        missions = DATABASE.ViewQuery('''SELECT missions.missionid, missions.userid, name, time_init, time_final, (time_final-time_init) AS duration, notes, count(*) AS victims FROM missions
            INNER JOIN users ON missions.userid = users.userid INNER JOIN sensor_log ON missions.missionid = sensor_log.missionid
            WHERE victim = 'True' GROUP BY missions.missionid''')
        return jsonify(missions)
    else:
        return render_template('missions.html')

@app.route('/missions-history')
def mission_history():
    return render_template('mission_data.html')


@app.route('/mission-data', methods = ['GET', 'POST'])
def mission_data():
    if request.method == 'POST':
        data = request.get_json()
        sensor_log = DATABASE.ViewQuery(f'SELECT * FROM sensor_log WHERE missionid = {data}')
        movement_log = DATABASE.ViewQuery(f'SELECT *, (time_final-time_init) AS duration FROM movement_log WHERE missionid = {data}')
        breakdown = DATABASE.ViewQuery(f'''SELECT missions.missionid, missions.userid, name, time_init, time_final, (time_final-time_init) AS duration, notes, count(*) AS victims FROM missions
            INNER JOIN users ON missions.userid = users.userid INNER JOIN sensor_log ON missions.missionid = sensor_log.missionid
            WHERE missions.missionid = {data} AND victim = 'True' GROUP BY missions.missionid''')
        details = {'sensor_data': sensor_log, 'movement_data': movement_log, 'breakdown': breakdown,
                'custom-graph': [{}], 'custom-table': [{}]}
        return jsonify(details)
    else:
        return redirect('/missions')

@app.route('/process_movement', methods = ['GET', 'POST'])
def process_movement():
    if request.method == 'POST':
        
        data = request.form.get('fd')
        print(data)
        current_keys = {'a': False,
            'w': False,
            's': False,
            'd': False,
            'space': False}
        if current_keys['space']:
            True
        elif current_keys['a'] and current_keys['w']:
            True#move_power(30, deviation=-10)
        elif current_keys['d'] and current_keys['w']:
            True#move_power(30, deviation=10)
        elif current_keys['a'] and current_keys['s']:
            True#move_power(-30, deviation=-10)
        elif current_keys['d'] and current_keys['s']:
            True#move_power(-30, deviation=10)
        elif current_keys['w']:
            True#move_power(30, 0)
        elif current_keys['s']:
            True#move_power(-30, 0)
        else:
            False#stop_all()
        #current_movements = session['movements']
        #movementIDs = current_movements.keys()
        #if movementID not in movementIDs:
            #new movement code
        #else:
            #
        return jsonify({})
    else:
        return redirect('/')


































# -----------------------------------------------------------------------------------
# CAMERA CODE-----------------------------------------------------------------------
# Continually gets the frame from the pi camera
def videostream():
    """Video streaming generator function."""
    while True:
        if GLOBALS.CAMERA:
            frame = GLOBALS.CAMERA.get_frame()
            if frame:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            else:
                return '', 204
        else:
            return '', 204 

#embeds the videofeed by returning a continual stream as above
@app.route('/videofeed')
def videofeed():
    log("READING CAMERA")
    if GLOBALS.CAMERA:
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(videostream(), mimetype='multipart/x-mixed-replace; boundary=frame') 
    else:
        return '', 204
        
#----------------------------------------------------------------------------
#Shutdown the robot, camera and database
def shutdowneverything():
    log("SHUT DOWN EVERYTHING")
    if GLOBALS.CAMERA:
        GLOBALS.CAMERA.stop()
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.safe_exit()
    GLOBALS.CAMERA = None; GLOBALS.ROBOT = None; GLOBALS.SOUND = None
    return

#Ajax handler for shutdown button
@app.route('/robotshutdown', methods=['GET','POST'])
def robotshutdown():
    shutdowneverything()
    return jsonify({'message':'robot shutdown'})

#Shut down the web server if necessary
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    shutdowneverything()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({'message':'Shutting Down'})

@app.route('/logout')
def logout():
    shutdowneverything()
    session.clear()
    return redirect('/')

#---------------------------------------------------------------------------
#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) #runs a local server on port 5000