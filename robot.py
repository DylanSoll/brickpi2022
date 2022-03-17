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


    def left_degrees(self, angle, power = 100, speed = 100):
        degrees = angle*2
        BP = self.BP
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, -1*power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, degrees +1)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, -1*degrees -1)
                time.sleep(0.02) 
                if BP.get_motor_encoder(BP.PORT_A) <= -1*degrees or BP.get_motor_encoder(BP.PORT_D) >= degrees:
                    break
                #print("A:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_A)))
                #print("D:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_D)))
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()
    
    def right_degrees(self, angle, power = 100, speed = 100):
        degrees = angle*2 
        BP = self.BP
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, -1*power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, -1*degrees-1)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, degrees+1)
                time.sleep(0.02) 
                if BP.get_motor_encoder(BP.PORT_A) >= degrees or BP.get_motor_encoder(BP.PORT_D) <= -1*degrees:
                    break
                #print("A:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_A)))
                #print("D:  " + str(distance+10) + "   " + str(BP.get_motor_encoder(BP.PORT_D)))
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()

    #Create a function to move time and power which will stop if colour is detected or wall has been found
    
    
    

    #Create a function to search for victim

    
    def return_new_direction(self, old_direction):
        print(old_direction)
        if old_direction == '+y':
            new_direction = '+x'
        elif old_direction == '+x':
            new_direction = '-y'
        elif old_direction == '-y':
            new_direction = '-x'
        elif old_direction == '-x':
            new_direction = '+y'
        print(new_direction)
        return new_direction

    def face_direction_coord(self, wall_to_search, current_direction):
        direction = wall_to_search.keys() #the first key in the dictionary is the direction
        for key in direction:
            direction = key
            break
        print(direction)
        target_heading = direction #use that to get the target direction
        while current_direction != target_heading:
            self.left_degrees(90)
            target_heading = self.return_new_direction(target_heading)
            print(target_heading)
        return target_heading


    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def search_maze(self):
        print('Initialising Search')
        #Initialise robot search variables
        sectors = {} # dictionary of all sectors of the maze
        current_sector = {'x':0, 'y':0} #robot starts at 0,0
        search = True #var for while loop
        #SEARCH CODE
        self.current_direction = "+y"
        while search:
            print(sectors)
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
                    
                    self.left_degrees(90)
                    self.current_direction = self.return_new_direction(self.current_direction)
                    status = False
                    while True:
                        print(self.get_ultra_sensor())
                        if self.get_ultra_sensor() < 20 and self.get_ultra_sensor() != 0: #there is a wall
                            status = True
                            print('Wall:' + str(status))
                            break
                    victim = False #predefines victim as false
                    temp_wall = {'status':False, 'victim': False, 'explored': False}
                    print()
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
                        if wall_to_search == None and (wall != 2 or current_sector_cp == '(0, 0)'):
                            temp_wall = {'status':False, 'victim': False, 'explored': True}
                            wall_to_search = {self.current_direction: temp_wall}
                            
                    print(temp_wall)
                    walls[self.current_direction] = temp_wall
                    if wall == 2 and current_sector_cp != "(0, 0)":
                        entered = wall
                if wall_to_search != None:
                    #update sector
                    self.current_direction = self.face_direction_coord(wall_to_search, self.current_direction)
                    old_x = current_sector['x']
                    old_y = current_sector['y']
                    print(old_x, old_y, self.current_direction)
                    if 'x' in self.current_direction:
                        new_y = old_y
                        if '-' in self.current_direction:
                            new_x = int(old_x) -1
                        elif '+' in self.current_direction:
                            new_x = int(old_x) + 1
                    elif 'y' in self.current_direction:
                        new_x = old_x
                        if '-' in self.current_direction:
                            new_y = int(old_y) -1
                        elif '+' in self.current_direction:
                            new_y = int(old_y) + 1
                    current_sector['x'] = new_x
                    current_sector['y'] = new_y
                    print(current_sector)
                    self.move_distance(40)
                print(walls)
                sectors[current_sector_cp]['walls'] = walls
                sectors[current_sector_cp]['entered'] = entered
                
            else:
                sector_complete = True
                walls = current_sector_vals['walls']
                indiv_walls = walls.keys()
                for wall_key in indiv_walls:
                    wall = walls[wall_key]
                    explored = wall['explored']
                    if explored == False:
                        sector_complete = False
                        direction = wall_to_search.keys() #the first key in the dictionary is the direction
                        for key in direction:
                            direction = key
                            break
                        
                        target_heading = direction #use that to get the target direction
                        while direction != target_heading:
                            self.left_degrees(90)
                            target_heading = self.return_new_direction(target_heading)
                    sectors[current_sector_cp]['walls'][wall_key]['explored'] = True
                    break
                if sector_complete and not current_sector_cp == "(0, 0)":
                    sectors[current_sector_cp]['complete'] = True
                    entered_by = sectors[current_sector_cp]['entered']
                    self.face_direction_coord(entered_by, self.current_direction)
                    self.move_distance(40)
                elif sector_complete == True and current_sector_cp == "(0, 0)":
                    print('Search Complete')
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
    #ROBOT.left_degrees(90)
    #time.sleep(1)
    ROBOT.search_maze()
    #ROBOT.right_degrees(90)
    #ROBOT.rotate_power_heading_IMU(15, 0, 35)
    ROBOT.safe_exit()
