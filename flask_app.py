from flask import Flask, render_template, session, request, redirect, flash, url_for, jsonify, Response, logging
from interfaces import databaseinterface, movement, soundinterface, camerainterface, emailinterface
import robot #robot is class that extends the brickpi class
import global_vars as GLOBALS #load global variables
import logging, time
import password_management as pm
#Creates the Flask Server Object
app = Flask(__name__); app.debug = True
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS
logging.basicConfig(filename='logs/flask.log', level=logging.INFO, format='Time: %(asctime)s Message: %(message)s')
GLOBALS.DATABASE = databaseinterface.DatabaseInterface('databases/U3_SIA2_Rescue_Database-V1.db', app.logger)
#Log messages
def log(message):
    app.logger.info(message)
    return


def please_login(current_address):
    if 'userid' not in session and current_address != 'login':
        return redirect('/login')
    elif 'permissions' in session:
        if session['permissions'] == 'pending' and current_address != 'pending':
            return redirect('/account/pending')
        elif session['permissions'] != 'admin' and current_address == 'admin':
            return redirect('/dashboard')
        elif current_address != 'dashboard':
            return redirect('/dashboard')
    return True

def reverse_sound(mode):
    if GLOBALS.SOUND:
        if mode:
            GLOBALS.SOUND.set_volume(.5)
            GLOBALS.SOUND.load_mp3("static/music/reversing_sx.mp3")
            GLOBALS.SOUND.play_music(-1)
        else:
            GLOBALS.SOUND.stop_music() 
    return
def play_song(song, times = 1, volume = 0.5):
    return_val = False
    if not GLOBALS.SOUND:
        GLOBALS.SOUND = soundinterface.SoundInterface()
    try:
        GLOBALS.SOUND.load_mp3(song)
        GLOBALS.SOUND.set_volume(volume)
        GLOBALS.SOUND.play_music(times)
        return_val = True
    except:
        return_val = False
    return return_val

#create a login page
@app.route('/', methods=['GET','POST'])
def redirect_on_entry():
    please_login('')
    return redirect('/login')


@app.route('/login', methods=['GET','POST'])
def login():
    please_login('login')
    if request.method == 'POST':
        email = str(request.form.get('login_email'))
        password = str(request.form.get('login_password'))
        userresults = GLOBALS.DATABASE.ViewQuery('SELECT * FROM users')
        if userresults != False:
            userresults = userresults[0]
            if pm.check_password(userresults['password'], password):
                session['userid'] = userresults['userid']
                session['name'] = userresults['name']
                session['email'] = userresults['email']
                session['permissions'] = userresults['permissions']
                return redirect('/dashboard')
    return render_template('login.html')


@app.route('/register', methods=["POST","GET"])
def register():
    please_login('login')
    if request.method == 'POST':
        email = str(request.form.get('email'))
        password = str(request.form.get('password'))
        name = str(request.form.get('fullName'))
        phoneNumber = str(request.form.get('phoneNumber'))
        hashedPassword = pm.hash_password(password)
        GLOBALS.DATABASE.ModifyQuery("INSERT INTO users (name,email, password, permissions, phone, pronouns) VALUES(?,?,?,?,?,?)",\
            (name,email, hashedPassword,'admin',phoneNumber, 'he/him'))
        userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))[0]
        session['userid'] = userdetails['userid']
        session['email'] = userdetails['email']
        session['permissions'] = userdetails['permissions']
        session['displayMode'] = userdetails['displayMode']
        return redirect('/')

    return render_template('register.html')

@app.route('/uniqueEmail', methods = ['POST', 'GET'])
def uniqueEmail():
    if request.method == "POST":
        email = request.get_json()
        print(email)
        result = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ? ", (email,))
        print(result)
        return jsonify(result)
    else:
        return redirect('/register')


@app.route('/admin')
def admin():
    please_login('admin')
    return render_template('admin.html')

@app.route('/get-users')
def get_users():
    if request.method == 'POST':
        info = request.get_json()
        users = GLOBALS.DATABASE.ViewQuery('''SELECT * FROM sensor_log WHERE missionid = ?''', (GLOBALS.MISSIONID,))[0]
        keys = users.keys()
        fields = ['select', 'useird', 'email', 'name', 'permissions', 'phone', 'pronouns']
        datasets = []
        for key in keys:
            datasets.append({'sensor':key, 'data':users[key]})
        return_val = {'datasets': datasets, 'fields': fields}
        return_val =  {'table_id':'users_table', 'columns':'info["columns"]', 'body_id': 'users_body_id','datasets': datasets, 'fields': fields}
        return jsonify(return_val)
    else:
        return redirect('/dashboard')
# Load the ROBOT
@app.route('/robotload', methods=['GET','POST'])
def robotload():
    sensordict = None
    if not GLOBALS.CAMERA:
        log("LOADING CAMERA")
        try:
            GLOBALS.CAMERA = camerainterface.CameraInterface()
        except Exception as error:
            log("FLASK APP: CAMERA NOT WORKING")
            GLOBALS.CAMERA = None
        if GLOBALS.CAMERA:
            GLOBALS.CAMERA.start()
    if not GLOBALS.ROBOT: 
        log("FLASK APP: LOADING THE ROBOT")
        GLOBALS.ROBOT = robot.Robot(20, app.logger)
        GLOBALS.ROBOT.configure_sensors() #defaults have been provided but you can 
        GLOBALS.ROBOT.reconfig_IMU()
    if not GLOBALS.SOUND:
        log("FLASK APP: LOADING THE SOUND")
        GLOBALS.SOUND = soundinterface.SoundInterface()
        GLOBALS.SOUND.say("I am ready")
    sensordict = GLOBALS.ROBOT.get_all_sensors()
    return jsonify(sensordict)

# ---------------------------------------------------------------------------------------
# Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def robotdashboard():
    please_login('dashboard')
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
    recent_sensor_data = {}
    if GLOBALS.ROBOT:
        recent_sensor_data = GLOBALS.ROBOT.get_all_sensors()
    elif GLOBALS.DATABASE:
        recent_sensor_data = GLOBALS.DATABASE.ViewQuery('SELECT * FROM sensor_log ORDER BY sensor_data_id DESC LIMIT 1')
    return jsonify(recent_sensor_data)

@app.route('/sensor-view', methods=['GET','POST'])
def sensor_view():
    if not GLOBALS.ROBOT:
        return render_template('sensors.html')
    else:
        return redirect('/dashboard')

# YOUR FLASK CODE------------------------------------------------------------------------

@app.route('/missions', methods = ['GET', 'POST'])
def missions():
    please_login('dashboard')
    if request.method == 'POST':
        missions = GLOBALS.DATABASE.ViewQuery('''SELECT missions.missionid, missions.userid, name, time_init, time_final, (time_final-time_init) AS duration, notes, count(*) AS victims FROM missions
            INNER JOIN users ON missions.userid = users.userid INNER JOIN sensor_log ON missions.missionid = sensor_log.missionid
            WHERE victim = 'True' GROUP BY missions.missionid''')
        return jsonify(missions)
    else:
        return render_template('mission_data.html')

@app.route('/initiate-mission', methods = ['GET', 'POST'])
def initiate_mission():
    if request.method == 'POST':
        if GLOBALS.DATABASE:
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO missions (userid, time_init) VALUES (?, ?)', (session['userid'], time.time()))
            GLOBALS.missionid = GLOBALS.DATABASE.ViewQuery('SELECT missionid FROM missions ORDER BY time_init DESC LIMIT 1')
        return jsonify({})
    return

@app.route('/save-mission', methods = ['GET', 'POST'])
def save_mission():
    if request.method == 'POST':
        notes = request.get_json()
        if GLOBALS.DATABASE:
            GLOBALS.DATABASE.ModifyQuery('''UPDATE missions SET time_final = ?, notes = ? WHERE missionid = (SELECT 
            missionid FROM missions ORDER BY time_init DESC LIMIT 1)''', (time.time(), notes))
            GLOBALS.MISSIONID = None
        return jsonify({})
    return

@app.route('/cancel-mission', methods = ['GET', 'POST'])
def cancel_mission():
    if request.method == 'POST':
        if GLOBALS.DATABASE:
            GLOBALS.DATABASE.ModifyQuery('''DELETE FROM missions WHERE missionid = ?''', (GLOBALS.MISSIONID,))
            GLOBALS.MISSIONID = None
        return jsonify({})
    return


@app.route('/mission-data', methods = ['GET', 'POST'])
def mission_data():
    if request.method == 'POST':
        data = request.get_json()
        sensor_log = GLOBALS.DATABASE.ViewQuery('SELECT * FROM sensor_log WHERE missionid = ?', (data,))
        movement_log = GLOBALS.DATABASE.ViewQuery('SELECT *, time_final-time_init AS duration FROM movement_log WHERE missionid = ?', (data,))
        breakdown = GLOBALS.DATABASE.ViewQuery('''SELECT missions.missionid, missions.userid, name, time_init, time_final, (time_final-time_init) AS duration, notes, count(*) AS victims FROM missions
            INNER JOIN users ON missions.userid = users.userid INNER JOIN sensor_log ON missions.missionid = sensor_log.missionid
            WHERE missions.missionid = ? AND victim = 'True' GROUP BY missions.missionid''', (data,))
        details = {'sensor_data': sensor_log, 'movement_data': movement_log, 'breakdown': breakdown,
                'custom-graph': [{}], 'custom-table': [{}]}
        return jsonify(details)
    else:
        return redirect('/missions')


@app.route('/sensor-graph-data', methods = ['GET', 'POST'])
def sensor_graph_data():
    if request.method == 'POST':
        data = request.get_json()
        sensor_log = GLOBALS.DATABASE.ViewQuery('SELECT * FROM sensor_log WHERE missionid = ?', (data,))
        return jsonify(sensor_log)
    else:
        return redirect('/missions')



@app.route('/sensor-live-data', methods = ['GET', 'POST'])
def sensor_live_data():
    if request.method == 'POST':
        if GLOBALS.MISSIONID != None:
            sensor_log = GLOBALS.DATABASE.ViewQuery('''SELECT acceleration, orientation, direction, distance, thermal, colour, 
            victim FROM sensor_log WHERE missionid = ?''', (GLOBALS.MISSIONID,))[0]
            keys = sensor_log.keys()
            fields = ['sensor', 'data']
            datasets = []
            for key in keys:
                datasets.append({'sensor':key, 'data':sensor_log[key]})
            return_val = {'datasets': datasets, 'fields': fields}
            return jsonify(return_val)
        else:
            return redirect('/dashboard')
    else:
        return redirect('/missions')


@app.route('/process_movement/<power>', methods = ['GET', 'POST'])
def process_movement(power):
    if request.method == 'POST':
        power = int(power)
        current_keys = request.get_json()
        if GLOBALS.ROBOT:
            GLOBALS.ROBOT.stop_all()
            if GLOBALS.MISSIONID != None:
                movement.end_time_movement()
            reverse_sound(False)
            log_move = True
            mov_type = ""
            if current_keys['stop']:
                GLOBALS.ROBOT.stop_all()
                log_move = False
            elif current_keys['w'] and not (current_keys['s']):
                if current_keys['a']:
                    GLOBALS.ROBOT.move_power(power, -1*int(power/2) + GLOBALS.DEVIATION)
                    mov_type = "forward-left"
                elif current_keys['d']:
                    GLOBALS.ROBOT.move_power(power, int(power/2) +GLOBALS.DEVIATION)
                    mov_type = "forward-right"
                else:
                    GLOBALS.ROBOT.move_power(power, GLOBALS.DEVIATION)
                    mov_type = "forward"
            elif current_keys['s'] and not (current_keys['w']):
                reverse_sound(True)
                if current_keys['a']:
                    GLOBALS.ROBOT.move_power(-power, -1*int(power/2) +GLOBALS.DEVIATION)
                    mov_type = "backward-left"
                elif current_keys['d']:
                    GLOBALS.ROBOT.move_power(-power, int(power/2) +GLOBALS.DEVIATION)
                    mov_type = "backward-right"
                else:
                    GLOBALS.ROBOT.move_power(-power, 0)
                    mov_type = "backward"
            elif current_keys['a'] and not current_keys['d']:
                GLOBALS.ROBOT.rotate_power(-1*power)
                mov_type = "left"
            elif current_keys['d'] and not current_keys['a']:
                GLOBALS.ROBOT.rotate_power(power)
                mov_type = "right"
            if log_move and (GLOBALS.MISSIONID != None):
                movement.log_movement(GLOBALS.MISSIONID, mov_type, time.time(), power, 'power', 'keyboard', False)
        return jsonify({})
    else:
        return redirect('/')


@app.route('/process_voice_commands', methods = ['GET', 'POST'])
def process_voice_commands():
    if request.method == 'POST':
        instructions = request.get_json()
        if GLOBALS.ROBOT:
            vc_type = instructions[0]
            magnitude = int(instructions[1])
            if vc_type == 'stop':
                GLOBALS.ROBOT.stop_all()
            elif vc_type == 'fire':
                GLOBALS.ROBOT.spin_medium_motor(1700)
            elif vc_type == 'left':
                power = instructions[3]
                GLOBALS.ROBOT.rotate_power_degrees_IMU(int(power/2), -1 * magnitude)
            elif vc_type == 'right':
                GLOBALS.ROBOT.rotate_power_degrees_IMU(int(power/2), magnitude)
            elif vc_type == 'face':
                GLOBALS.ROBOT.rotate_power_heading_IMU(int(power/2), magnitude)
            elif vc_type == 'forward':
                GLOBALS.ROBOT.move_power_time(power, magnitude, GLOBALS.DEVIATION)
            elif vc_type == 'backward':
                reverse_sound(True)
                GLOBALS.ROBOT.move_power_time(-1*power, magnitude, GLOBALS.DEVIATION)
                reverse_sound(False)
            elif vc_type == 'play':
                play_song('static/music/8_9_10_MP3_song.mp3',1,0.5)
        return jsonify(instructions)
    else:
        return redirect('/')

@app.route('/process_shooting', methods = ['GET', 'POST'])
def process_shooting():
    if request.method == 'POST':
        if GLOBALS.ROBOT:
            GLOBALS.ROBOT.spin_medium_motor(1700)
        return jsonify({})
    else:
        return redirect('/')

@app.route('/btn-mov/<mov_type>/<power>', methods = ['GET', 'POST'])
def btn_movements(mov_type, power):
    if request.method == 'POST':
        if GLOBALS.ROBOT: 
            power = int(power)
            log_move = True
            if GLOBALS.MISSIONID != None:
                movement.end_time_movement()
            if mov_type == 'stop':
                GLOBALS.ROBOT.stop_all()
            elif mov_type == 'left':
                GLOBALS.ROBOT.rotate_power(int(power/2))
            elif mov_type == 'right':
                GLOBALS.ROBOT.rotate_power(-1*int(power/2))
            elif mov_type == 'forward':
                GLOBALS.ROBOT.move_power(power)
            elif mov_type == 'backward':
                reverse_sound(True)
                GLOBALS.ROBOT.move_power(-1*power)
                reverse_sound(False)
            elif mov_type == 'play':
                log_move = False
                play_song('static/music/8_9_10_MP3_song.mp3',1,0.5)
            else:
                log_move = False
            if log_move and (GLOBALS.MISSIONID != None):
                movement.log_movement(GLOBALS.MISSIONID, mov_type, time.time(), power, 'power', 'button', False)
        return jsonify(mov_type)
    else:
        return redirect('/')


@app.route('/account', methods = ['POST', 'GET'])
def account():
    #please_login('pending')
    return render_template('account.html')
    

@app.route('/reverse')
def reverse():
    if request.method == 'POST':
        if GLOBALS.ROBOT and GLOBALS.DATABASE:
            movement.reverse_path(GLOBALS.MISSIONID)
        return jsonify({})
    return redirect('/dashboard')


@app.route('/create-graphs', methods = ['POST', 'GET'])
def create_graphs():
    if request.method == 'POST':
        parsed_details = request.get_json()
        print(parsed_details)
        time_frame = parsed_details['time']
        #SQL_query = "SELECT * FROM sensor_log INNER JOIN missions on missions.missionid = sensor_log.missionid INNER JOIN users on missions.userid = users.userid"
        '''if time_frame != False:
            start_time = time_frame['start']
            end_time = time_frame['end']
            if start_time != False:
                ""'''

        details = "{'table_id', 'columns', 'body_id', 'data', 'fields'}"
        details = {}
        return jsonify(details)
    else:
        return redirect('/missions')


























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
    if GLOBALS.CAMERA:
        log("FLASK APP: READING CAMERA")
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(videostream(), mimetype='multipart/x-mixed-replace; boundary=frame') 
    else:
        return '', 204
        
#----------------------------------------------------------------------------
#Shutdown the robot, camera and database
def shutdowneverything():
    log("FLASK APP: SHUTDOWN EVERYTHING")
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
    return redirect('/login')

#---------------------------------------------------------------------------
#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) #runs a local server on port 5000
