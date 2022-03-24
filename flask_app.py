from collections import UserString
from flask import Flask, render_template, session, request, redirect, jsonify, flash, url_for, Response, logging
from json import dumps
from interfaces import databaseinterface, movement, emailinterface
try:
    import robot#robot is class that extends the brickpi class
    from interfaces import soundinterface, camerainterface
     
except:
    print('failed')
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

def confirm_movement_perms(): 
    if GLOBALS.ControllerID and 'userid' in session:
        if GLOBALS.ControllerID == session['userid']:
            return True
    return False

def log_movement(missionid, mov_type, time_init, power, movement_type, command_type, magnitude = False):
    if GLOBALS.DATABASE:
        GLOBALS.DATABASE.ModifyQuery('''INSERT INTO movement_log (missionid, type, time_init, magnitude, power,
         movement_type, command_type) VALUES (?, ?, ?, ?, ?, ?, ?)''', \
             (missionid, mov_type, time_init, magnitude, power, movement_type, command_type))
        print(GLOBALS.DATABASE.ViewQuery('SELECT * FROM movement_log WHERE missionid = (SELECT missionid FROM missions ORDER BY missionid DESC LIMIT 1)'))
    return

def log_sensors(missionid, acceleration, orientation, direction, distance, thermal, colour, victim, time):
    if GLOBALS.DATABASE:
        GLOBALS.DATABASE.ModifyQuery('''INSERT INTO sensor_log (missionid, acceleration, orientation, direction, distance, 
        thermal, colour, victim, time) VALUES (?, ?, ?, ?, ?, ?, ?,?,?)''', \
             (missionid, acceleration, orientation, direction, distance, thermal, colour, victim, time))
        
    return

def end_time_movement():
    if GLOBALS.DATABASE:
        print('hit')
        GLOBALS.DATABASE.ModifyQuery('''UPDATE movement_log SET time_final = ? WHERE movementid = 
        (SELECT movementid FROM movement_log WHERE time_final IS NULL ORDER BY time_init DESC LIMIT 1)''', (time.time(),))

    return

def please_login(current_address):
    """Redirects user based on permissions, login status and current location

    Args:
        current_address (str): Users current location

    """    
    if 'userid' not in session and current_address != 'login':
        return redirect('/login')
    if 'permissions' in session:
        if session['permissions'] == 'pending' and current_address != 'pending':
            return redirect('/account/pending')
        elif current_address != 'dashboard':
            return redirect('/dashboard')
    return

def reverse_sound(mode):
    """Stops or plays reverse sound effect

    Args:
        mode (bool): Start of stop reversing sound
    """    
    if GLOBALS.SOUND: #checks to see if GLOBALS.SOUND works
        if mode: #if True
            GLOBALS.SOUND.set_volume(.5) #sets volume
            GLOBALS.SOUND.load_mp3("static/music/reversing_sx.mp3") #loads sound
            GLOBALS.SOUND.play_music(-1) #plays reverse beep infinitely
        else:
            GLOBALS.SOUND.stop_music() #otherwise stop playing
    return


def play_song(song, times = 1, volume = 0.5):
    """Plays song x number of times and volume

    Args:
        song (str): Filename and directory of song
        times (int, optional): How many times the song is played. -1 is on repeat. Defaults to 1.
        volume (float, optional): Volume of the speaker. Defaults to 0.5.

    Returns:
        bool: Whether or not song is played
    """    
    try: #tries to play music
        if not GLOBALS.SOUND: #if sound not defined
            GLOBALS.SOUND = soundinterface.SoundInterface() #create new instance
        GLOBALS.SOUND.load_mp3(song) #loads specified song
        GLOBALS.SOUND.set_volume(volume) #sets volume of speaker
        GLOBALS.SOUND.play_music(times) #plays song specified number of times
        return_val = True #if no errors, music played successfully
    except:#if failed
        return_val = False #song not played successfully
    return return_val

#create a login page
@app.route('/', methods=['GET','POST'])
def redirect_on_entry():
    please_login('')
    return redirect('/dashboard')


@app.route('/login', methods=['GET','POST'])
def login():
    if 'userid' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        email = str(request.form.get('login_email'))
        password = str(request.form.get('login_password'))
        userresults = GLOBALS.DATABASE.ViewQuery('SELECT * FROM users WHERE email = ?', (email,))
        if userresults != False:
            userresults = userresults[0]
            if pm.check_password(userresults['password'], password):
                session['userid'] = userresults['userid']
                session['name'] = userresults['name']
                session['email'] = userresults['email']
                session['permissions'] = userresults['permissions']
                if userresults['userid'] == 1:
                    GLOBALS.ControllerID = userresults['userid']
                elif not GLOBALS.ControllerID:
                    GLOBALS.ControllerID = userresults['userid']
                return redirect('/dashboard')
    return render_template('login.html')


@app.route('/register', methods=["POST","GET"])
def register():
    if 'userid' in session:
        return redirect('/dashboard')
    if request.method == 'POST':
        email = str(request.form.get('email'))
        password = str(request.form.get('password'))
        name = str(request.form.get('fullName'))
        phoneNumber = str(request.form.get('phoneNumber'))
        hashedPassword = pm.hash_password(password)
        GLOBALS.DATABASE.ModifyQuery("INSERT INTO users (name,email, password, permissions, phone, pronouns) VALUES(?,?,?,?,?,?)",\
            (name,email, hashedPassword,'pending',phoneNumber, 'he/him'))
        userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))[0]
        session['userid'] = userdetails['userid']
        session['email'] = userdetails['email']
        session['permissions'] = userdetails['permissions']
        session['displayMode'] = userdetails['displayMode']
        return redirect('/')

    return render_template('register.html')




@app.route('/admin')
def admin():
    if session['permissions'] != 'admin':
        return redirect('/dashboad')
    return render_template('admin.html')

@app.route('/get-users', methods = ['GET', 'POST'])
def get_users():
    if request.method == 'POST':
        info = request.get_json()
        users = GLOBALS.DATABASE.ViewQuery('''SELECT * FROM users''')
        if users:
            datasets = []
            for user in users:
                row = {}
                fields = ['select', 'userid', 'email', 'name', 'permissions', 'phone', 'pronouns']
                for field in fields:
                    if field == 'select':
                        row[field] = 'select'
                    else:
                        row[field] = user[field]
                datasets.append(row)
                
            return_val =  {'table_id':'users_table', 'columns':info["columns"], 'body_id': 'users_body_id','datasets': datasets, 'fields': fields}

        return dumps(return_val)
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
        try:
            log("FLASK APP: LOADING THE ROBOT")
            GLOBALS.ROBOT = robot.Robot(20, app.logger)
            GLOBALS.ROBOT.configure_sensors() #defaults have been provided but you can 
            GLOBALS.ROBOT.reconfig_IMU()
        except:
            pass
    if not GLOBALS.SOUND:
        try:
            log("FLASK APP: LOADING THE SOUND")
            GLOBALS.SOUND = soundinterface.SoundInterface()
            GLOBALS.SOUND.say("I am ready")
        except:
            pass
    if GLOBALS.ROBOT:
        sensordict = GLOBALS.ROBOT.get_all_sensors()
    else:
        sensordict = {}
    return dumps(sensordict)

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
    recent_sensor_data = False
    if GLOBALS.ROBOT:
        recent_sensor_data = GLOBALS.ROBOT.get_all_sensors()
        if GLOBALS.MISSIONID:
            victim = False
            distance = recent_sensor_data['ultrasonic']
            distance = 0
            log_sensors(str(GLOBALS.MISSIONID), str(recent_sensor_data['acceleration']), str(recent_sensor_data['orientation']), str(recent_sensor_data['gyro']), 
            str(distance),str(recent_sensor_data['thermal']), str(recent_sensor_data['colour']),str(victim), 
            str(time.time()))
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
        missions = GLOBALS.DATABASE.ViewQuery('''SELECT missionid, name, time_init, time_final, notes, (time_final-time_init) AS duration, name FROM missions
            INNER JOIN users ON missions.userid = users.userid WHERE time_final NOT NULL GROUP BY missions.missionid''')
        return dumps(missions)
    else:
        return render_template('mission_data.html')

@app.route('/initiate-mission', methods = ['GET', 'POST'])
def initiate_mission():
    if request.method == 'POST':
        if GLOBALS.DATABASE:
            ######
                #Delete Broken Missions
            ######
            GLOBALS.DATABASE.ModifyQuery('DELETE FROM missions WHERE time_final IS NULL')
            GLOBALS.DATABASE.ModifyQuery('DELETE FROM sensor_log WHERE missionid NOT IN (SELECT missionid FROM missions)')
            GLOBALS.DATABASE.ModifyQuery('DELETE FROM movement_log WHERE missionid NOT IN (SELECT missionid FROM missions)')
            ##########
            ##########
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO missions (userid, time_init) VALUES (?, ?)', (session['userid'], time.time()))
            GLOBALS.MISSIONID = (GLOBALS.DATABASE.ViewQuery('SELECT missionid FROM missions ORDER BY time_init DESC LIMIT 1'))[0]['missionid']
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
        breakdown = GLOBALS.DATABASE.ViewQuery('''SELECT missionid, name, time_init, time_final, notes, (time_final-time_init) AS duration, name FROM missions
            INNER JOIN users ON missions.userid = users.userid WHERE missionid = ?''', (data,))
        details = {'sensor_data': sensor_log, 'movement_data': movement_log, 'breakdown': breakdown,
                'custom-graph': [{}], 'custom-table': [{}]}
        return dumps(details)
    else:
        return redirect('/missions')

@app.route('/images')
def images():
    please_login('dashboard')
    return render_template('images.html')



@app.route('/sensor-graph-data', methods = ['GET', 'POST'])
def sensor_graph_data():
    if request.method == 'POST':
        data = request.get_json()
        sensor_log = GLOBALS.DATABASE.ViewQuery('SELECT * FROM sensor_log WHERE missionid = ?', (data,))
        return dumps(sensor_log)
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
            return dumps(return_val)
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
                end_time_movement()
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
                log_movement(GLOBALS.MISSIONID, mov_type, time.time(), power, 'power', 'keyboard', False)
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
            if GLOBALS.MISSIONID != None:
                end_time_movement()
            power = int(power)
            log_move = True
            if mov_type == 'stop':
                GLOBALS.ROBOT.stop_all()
            elif mov_type == 'left':
                GLOBALS.ROBOT.rotate_power(-1*int(power/2))
            elif mov_type == 'right':
                GLOBALS.ROBOT.rotate_power(int(power/2))
            elif mov_type == 'forward':
                GLOBALS.ROBOT.move_power(power)
            elif mov_type == 'back':
                reverse_sound(True)
                GLOBALS.ROBOT.move_power(-1*power)
                reverse_sound(False)
            elif mov_type == 'play':
                log_move = False
                play_song('static/music/8_9_10_MP3_song.mp3',1,0.5)
            else:
                log_move = False
            if log_move and (GLOBALS.MISSIONID != None):
                log_movement(GLOBALS.MISSIONID, mov_type, time.time(), power, 'power', 'button', False)
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
            frame = GLOBALS.CAMERA.collect_live_frame()#get_frame()#
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


@app.route('/take-photo', methods = ['GET', 'POST'])
def take_photo():
    if GLOBALS.CAMERA and request.method=='POST':
        data = GLOBALS.CAMERA.take_photo()
        if GLOBALS.DATABASE:
            #print(data['raw_image'])
            if GLOBALS.MISSIONID:
                GLOBALS.DATABASE.ModifyQuery('''INSERT INTO images (image, userid, time, missionid, raw_image, colour_lower,
                    colour_upper) VALUES (?,?,?,?,?,?,?)''', (data['image'], session['userid'], \
                        data['time_taken'], GLOBALS.MISSIONID, data['raw_image'], str(data['lower_col']), str(data['upper_col'])))
            else:
                GLOBALS.DATABASE.ModifyQuery('''INSERT INTO images (image, userid, time, raw_image, colour_lower, 
                    colour_upper) VALUES (?,?,?,?,?,?)''', (data['image'], session['userid'], \
                        data['time_taken'], data['raw_image'], str(data['lower_col']), str(data['upper_col'])))
        return jsonify({})
    else:
        return redirect('/dashboard')
@app.route('/display_image/<imageid>/<altered>')
def display_image(imageid, altered):
    if GLOBALS.DATABASE:
        image_data = GLOBALS.DATABASE.ViewQuery('SELECT * FROM images WHERE imageid = ?', (imageid,))
        if image_data:
            image = image_data[0]['image']
            if altered == 'true':
                image = image_data[0]['image']
            elif altered == 'false':
                image = image_data[0]['raw_image']
            return Response((b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n'),mimetype='multipart/x-mixed-replace; boundary=frame') 
        else:
            return '', 204
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


#AJAX request functions
@app.route('/uniqueEmail', methods = ['POST', 'GET'])
def uniqueEmail():
    if request.method == "POST":
        email = request.get_json()
        result = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ? ", (email,))
        return jsonify(result)
    else:
        return redirect('/register')

@app.route('/image-details', methods = ['GET', 'POST'])
def get_image_details():
    if request.method == 'POST':
        data = request.get_json()
        print(data['columns'])
        fields = ['select', 'imageid', 'image', 'raw_image', 'time', 'name']
        image_data = GLOBALS.DATABASE.ViewQuery('SELECT imageid, image, name, time, raw_image FROM images INNER JOIN \
            users on images.userid = users.userid')
        if image_data:
            datasets = []
            for images in image_data:
                row = {}
                for field in fields:
                    if field == 'select':
                        row[field] = 'select'
                    elif field == 'image':
                        row[field] = "/display_image/"+str(images['imageid'])+"/true"
                    elif field == 'raw_image':
                        if images['raw_image'] != '':
                            row[field] = "/display_image/"+str(images['imageid'])+"/false"
                        else:
                            row[field] = "/display_image/"+str(images['imageid'])+"/true"
                    else:
                        row[field] = images[field]
                datasets.append(row)
            data['datasets'] = datasets
            data['fields'] = fields
            return dumps(data)
        return jsonify({})
    return

@app.route('/update-colour-mask/<colour_target>', methods = ['GET', 'POST'])
def update_colour_mask(colour_target):
    if request.method == 'POST':
        hex = request.get_json()
        col = hex.lstrip('#')
        col = tuple(int(col[i:i+2], 16) for i in (0, 2, 4))
        if GLOBALS.CAMERA:
            if colour_target == 'lower':
                GLOBALS.CAMERA.lower_col = (col[2], col[1], col[0])
            elif colour_target == 'upper':
                GLOBALS.CAMERA.upper_col = (col[2], col[1], col[0])
        return jsonify({})
        
    else:
        return redirect('/dashboard')
@app.route('/say-phrase', methods = ['GET', 'POST'])
def say_phrase():
    if request.method == 'POST':
        phrase = request.get_json()
        if GLOBALS.SOUND:
            GLOBALS.SOUND.say(phrase)
            return jsonify('Said: ' + phrase)
        else:
            return jsonify('Sound not connected')
        
    else:
        return redirect('/dashboard')

@app.route('/get-battery', methods = ['GET', 'POST'])
def get_battery():
    if request.method == 'POST':
        if GLOBALS.ROBOT:
            battery = (GLOBALS.ROBOT.get_battery()*100)/12
            return jsonify(battery)
        else:
            battery = 0
            return jsonify(battery)
        
    else:
        return redirect('/dashboard')


@app.route('/move-distance', methods = ['GET', 'POST'])
def move_distance():
    if request.method == 'POST':
        value = request.get_json()
        if GLOBALS.ROBOT:
            GLOBALS.ROBOT.move_distance(value)
        else:
            return redirect('Failed')
        
    else:
        return redirect('/dashboard')

@app.route('/turn_degrees/<direction>', methods = ['GET', 'POST'])
def turn_degrees(direction):
    if request.method == 'POST':
        value = request.get_json()
        if GLOBALS.ROBOT:
            if direction == 'right':
                GLOBALS.ROBOT.right_degrees(value)
            elif direction == 'left':
                GLOBALS.ROBOT.left_degrees(value)
        else:
            return redirect('Failed')
        
    else:
        return redirect('/dashboard')
@app.route('/autosearch', methods = ['GET', 'POST'])
def autosearch():
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.search_maze()
    return jsonify({})
#----------------------------------------
#---------------------------------------------------------------------------
#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) #runs a local server on port 5000
