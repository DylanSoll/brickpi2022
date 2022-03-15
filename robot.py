#This is where your main robot code resides. It extendeds from the BrickPi Interface File
#It includes all the code inside brickpiinterface. The CurrentCommand and CurrentRoutine are important because they can keep track of robot functions and commands. Remember Flask is using Threading (e.g. more than once process which can confuse the robot)
from interfaces.brickpiinterface import *
import global_vars as GLOBALS
import logging
import numpy as np

class Robot(BrickPiInterface):
    
    def __init__(self, timelimit=10, logger=logging.getLogger()):
        super().__init__(timelimit, logger)
        self.CurrentCommand = "stop" #use this to stop or start functions
        self.CurrentRoutine = "stop" #use this stop or start routines
        return
            

    def move_distance(self, distanceCm, power = 30, speed=100, canTimeOut = False):
        """Moves the robot a specified distance

        Args:
            distanceCm (int): Distance for robot to travel in cm (positive for forward, negative for back)
            power (int, optional): Power of robots motors (%). Defaults to 30.
            speed (int, optional): Speed of robots motors (degrees pe second). Defaults to 100.
            canTimeOut (bool, optional): Does move_distance have a time limit. Defaults to False.

        Returns:
            dict: python dictionary with distanceCm, time_init, time_final, duration
        """        
        self.interrupt_previous_command() #stops previous command
        self.CurrentCommand = "move_distance" #sets current command to move_distance
        distance = (distanceCm * 360) / (np.pi * 5.6) #converts distance (cm) to rotations
        BP = self.BP #creates local var of BrickPi
        BP.set_motor_power(self.rightmotor, power) #sets left and right motor
        BP.set_motor_power(self.leftmotor, power) 
        time_init = time.time() #gets start time
        return_val = "error" #declares return val (if no error, redefined later)
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, power, speed)  # sets power (%) and speed limit (degrees/s)
            BP.set_motor_limits(BP.PORT_D, power, speed)  # sets power (%) and speed limit (degrees/s)
            run = True #defines run as true
            while run: #while true
                if distanceCm > 0: #if distance is positive, increase motor position
                    BP.set_motor_position(BP.PORT_D, distance+10)
                    BP.set_motor_position(BP.PORT_A, distance+10)
                else: #else distance is negative, so decrease motor position
                    BP.set_motor_position(BP.PORT_D, distance-10)   
                    BP.set_motor_position(BP.PORT_A, distance-10)
                time.sleep(0.01) #sleeps for 0.01 second to protect Brick Pi
                if BP.get_motor_encoder(BP.PORT_D) >= distance or BP.get_motor_encoder(BP.PORT_A) >= distance: 
                    run = False #if Brick Pi has moved the necessary distance, end while loop
                elif self.CurrentCommand != 'move_distance':
                    run = False #allows for self.interrupt_previous_command
                elif (self.timelimit + time_init) >= time.time() and canTimeOut:
                    run = False #allows for time_limit
            time_final = time.time() #saves time final and duration
            duration = time_final - time_init
            return_val = {'distance':distanceCm, 'time_init': time_init, 'time_final': time_final, 'duration': duration}
            #redefines return_Val as an array of distance, start and finish time, and duration
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all() #reset robot motors
        return return_val #returns return val


    def right_degrees(self, angle, power = 100, speed = 100):
        degrees = angle*2 +5
        BP = ROBOT.BP
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, -1*power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, degrees+10)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, -1*degrees-10)
                time.sleep(0.02) 
                if BP.get_motor_encoder(BP.PORT_D) >= degrees or BP.get_motor_encoder(BP.PORT_A) <= -1*degrees:
                    break
                #print("A:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_A)))
                #print("D:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_D)))
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()
        return
    
    def left_degrees(self, angle, power = 100, speed = 100):
        degrees = angle*2 + 5
        BP = ROBOT.BP
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, -1*power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, -1*degrees-10)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, degrees+10)
                time.sleep(0.02) 
                if BP.get_motor_encoder(BP.PORT_A) >= degrees or BP.get_motor_encoder(BP.PORT_D) <= -1*degrees:
                    break
                #print("A:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_A)))
                #print("D:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_D)))
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()

    #Create a function to move time and power which will stop if colour is detected or wall has been found
    
    
    

    #Create a function to search for victim
    
    def clean_heading(self,heading):
        if heading >= 360:
            heading -= 360
        elif heading <= 360:
            heading += 360
        return heading
    
    def face_heading(self, heading):
        direction = self.get_compass_IMU()
        print(direction)
        print(heading)
        if heading > direction:
            self.left_degrees(direction-heading)

        else:
            self.right_degrees(direction-heading)

        return 
    
    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def search_maze(self):
        print('Initialising Search')
        #Initialise robot search variables
        sectors = {} # dictionary of all sectors of the maze
        heading = self.get_compass_IMU() #gets initial heading
        coordinate_headings = {'+y':self.clean_heading(heading), '+x': self.clean_heading(heading)+90,
        '-y':self.clean_heading(heading) + 180, '-x': self.clean_heading(heading)+270} #has specific bearings for each heading
        current_sector = {'x':0, 'y':0} #robot starts at 0,0
        search = True #var for while loop
        #SEARCH CODE
        while search:
            current_sector_cp = '('+str(current_sector['x'])+', '+str(current_sector['y'])+')'
            if current_sector_cp in sectors:
                current_sector_vals = sectors[current_sector_cp]
            else:
                current_sector_vals = None
            if not current_sector_vals:
                walls = {} #creates a blank list for all the walls
                wall_to_search = None #the wall that is to be searched first
                for wall in range(4): #up to 4 walls per box
                    ##for each wall
                    self.reconfig_IMU()
                    current_heading = self.get_compass_IMU()
                    print(current_heading)
                    current_direction = None
                    for direction in coordinate_headings.keys():
                        current_direction = direction
                        direct_val = coordinate_headings[direction]
                        if direct_val - 5 < direct_val < direct_val + 5:
                            current_heading = direct_val
                            break
                    self.left_degrees(90)
                    status = False
                    if self.get_ultra_sensor() < 20: #there is a wall
                        status = True
                        print('Wall:' + str(status))
                    victim = False #predefines victim as false
                    if status == True: #if wall
                        if GLOBALS.CAMERA:
                            h = GLOBALS.CAMERA.find_h(GLOBALS.CAMERA.data)
                            if h:
                                self.spin_medium_motor(1200)
                                victim = 'H'
                            else: #U can sometimes be detected in H, so if no H
                                u = GLOBALS.CAMERA.find_u(GLOBALS.CAMERA.data)
                                if u:
                                    victim = 'U'
                                    if GLOBALS.SOUND:
                                        GLOBALS.SOUND.say('Medical professionals will be with you shortly')
                        temp_wall = {'status':status, 'victim': victim, 'explored': False}
                    
                    elif status == False:#must be no wall
                        if wall_to_search == None:
                            temp_wall = {'status':False, 'victim': False, 'explored': True}
                            wall_to_search = {current_direction: current_heading}
                        else:
                            temp_wall = {'status':False, 'victim': False, 'explored': False}
                    print(temp_wall)
                    walls[current_direction] = temp_wall
                if wall_to_search != None:
                    #update sector
                    direction = wall_to_search.keys()[0] #the first key in the dictionary is the direction
                    target_heading = wall_to_search[direction] #use that to get the target direction
                    old_x = current_sector['x']
                    old_y = current_sector['y']
                    if 'x' in direction:
                        new_y = old_y
                        if '-' in direction:
                            new_x = int(old_x) -1
                        elif '+' in direction:
                            new_x = int(old_x) + 1
                    elif 'y' in direction:
                        new_x = old_x
                        if '-' in direction:
                            new_y = int(new_y) -1
                        elif '+' in direction:
                            new_y = int(new_y) + 1
                    current_sector['x'] = new_x
                    current_sector['y'] = new_y
                    print(current_sector)
                    self.rotate_power_heading_IMU(15, target_heading)
                    self.move_distance(40)
                sectors[current_sector_cp] = walls
            else:
                walls = current_sector_vals
                indiv_walls = walls.keys()
                for wall_key in indiv_walls:
                    wall = walls[wall_key]
                    explored = wall['explored']
                    if explored == False:
                        current_heading = coordinate_headings[wall_key]
                        self.rotate_power_heading_IMU(15, self.clean_heading(current_heading))
                    sectors[current_sector_cp][wall_key]['explored'] = True
                    break
                if explored == True and current_sector_cp == "(0, 0)":
                    print('break')
                    search = False
        print(sectors)

        ##ON TERMINATION
        if GLOBALS.SOUND:
            GLOBALS.SOUND.say('Search Complete')
        ##LOG EVERYTHING TO DATABASE
        return





# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logging.basicConfig(filename='logs/robot.log', level=logging.INFO)
    ROBOT = Robot(timelimit=10)  #10 second timelimit before
    ROBOT.configure_sensors() #This takes 4 seconds
    #ROBOT.rotate_power_degrees_IMU(20,-90)
    ROBOT.search_maze()

    ROBOT.safe_exit()
