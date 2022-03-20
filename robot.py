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
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()

    #Create a function to move time and power which will stop if colour is detected or wall has been found
    
    
    

    #Create a function to search for victim

    
    def return_new_direction(self, old_direction, turning = 'left'):

        if turning == 'left':
            if old_direction == '+y':
                new_direction = '+x'
            elif old_direction == '+x':
                new_direction = '-y'
            elif old_direction == '-y':
                new_direction = '-x'
            elif old_direction == '-x':
                new_direction = '+y'
        elif turning == 'right':
            if old_direction == '+y':
                new_direction = '-x'
            elif old_direction == '-x':
                new_direction = '-y'
            elif old_direction == '-y':
                new_direction = '+x'
            elif old_direction == '+x':
                new_direction = '+y'
        return new_direction

    def face_direction_coord(self, wall_to_search, current_direction):
        direction = wall_to_search.keys() #the first key in the dictionary is the direction
        for key in direction:
            direction = key
            break
        target_heading = direction #use that to get the target direction
        while current_direction != target_heading:
            self.left_degrees(90)
            target_heading = self.return_new_direction(target_heading)
        return target_heading

    def get_new_xy(self, direction, coordinate):
        old_x, old_y = coordinate[1,-1].split(', ')
        if 'x' in direction:
            new_y = old_y
            if '-' in direction:
                new_x = int(old_x) -1
            elif '+' in direction:
                new_x = int(old_x) + 1
        elif 'y' in direction:
            new_x = old_x
            if '-' in direction:
                new_y = int(old_y) -1
            elif '+' in direction:
                new_y = int(old_y) + 1
        return new_x, new_y

    def update_sector_cp(self, direction):
        old_x = self.current_sector['x']
        old_y = self.current_sector['y']
        if 'x' in direction:
            new_y = old_y
            if '-' in direction:
                new_x = int(old_x) -1
            elif '+' in direction:
                new_x = int(old_x) + 1
        elif 'y' in direction:
            new_x = old_x
            if '-' in direction:
                new_y = int(old_y) -1
            elif '+' in direction:
                new_y = int(old_y) + 1
        self.current_sector['x'] = new_x
        self.current_sector['y'] = new_y
        return direction

    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def search_new_sector(self, current_sector_cp):
        print(current_sector_cp)
        walls = {} #creates a blank list for all the walls
        wall_to_search = None #the wall that is to be searched first
        for wall in range(4): #up to 4 walls per box
            ##for each wall
            self.left_degrees(90)
            self.current_direction = self.return_new_direction(self.current_direction)
            status = False
            tries = 0
            while True:
                if self.get_ultra_sensor() < 25 and self.get_ultra_sensor() not in [0,999]: #there is a wall
                    status = True
                    print('Wall:' + str(status))
                    break
                elif self.get_ultra_sensor() not in [0,999]:
                    break
                tries +=1
                if tries == 5:
                    status = True
                    break
                print('test')
            victim = False #predefines victim as false
            temp_wall = {'status':False, 'victim': False, 'explored': False}
            print('Trial')
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
                if wall_to_search == None and not (wall == 2 or current_sector_cp == '(0, 0)'):
                    temp_wall = {'status':False, 'victim': False, 'explored': True}
                    wall_to_search = {self.current_direction: temp_wall}
            
            walls[self.current_direction] = temp_wall
            if wall == 2 and current_sector_cp != "(0, 0)":
                entered = temp_wall
            print(temp_wall)
        if wall_to_search != None:
            #update sector
            self.current_direction = self.face_direction_coord(wall_to_search, self.current_direction)
            self.current_direction = self.update_sector_cp(self.current_direction)
            self.move_distance(40)
        self.sectors[current_sector_cp] = {'walls': {}, 'entered':{}, 'complete': False}

        self.sectors[current_sector_cp]['walls'] = walls
        if current_sector_cp == "(0, 0)":
            self.sectors[current_sector_cp]['entered'] = False
        else:
            self.sectors[current_sector_cp]['entered'] = entered
        return

    def search_old_sector(self, current_sector_cp):
        cont_search = True
        walls = self.sectors[current_sector_cp]['walls']
        entered_from = self.sectors[current_sector_cp]['entered']
        wall_keys = walls.keys()
        possible_movement = None
        for key in wall_keys:
            wall = walls[key]
            if wall['status'] == False and wall['explored'] == False:
                possible_movement = key
                self.sectors[current_sector_cp]['walls'][key]['explored'] = True
                self.current_direction = self.face_direction_coord({key:wall}, self.current_direction)
                self.move_distance(40)
                self.current_direction = self.update_sector_cp(self.current_direction)
                break
        if possible_movement == None and current_sector_cp == '(0, 0)':
            cont_search = False
            self.sectors[current_sector_cp]['complete'] = True
        elif possible_movement == None:
            self.current_direction = self.face_direction_coord(entered_from, self.current_direction)
            self.move_distance(40)
            self.current_direction = self.update_sector_cp(self.current_direction)
            self.sectors[current_sector_cp]['complete'] = True
        return cont_search

    def scan_maze_logs(self):
        directions = []
        sector_coords = self.sectors.keys()
        for coord in sector_coords:
            sector = self.sectors[coord]
            if sector['complete']:
                break
            else:
                
                for wall in sector['walls'].keys():
                    wall_dict = sector['walls'][wall]
                    if wall_dict['status'] and not wall_dict['explored']:
                        new_coord = coord
                        while True:
                            for sect in sector['entered'].keys():
                                directions.append(sect)
                            new_coord = self.get_new_xy(sect, new_coord)
                            if new_coord == "(0, 0)":
                                break
                        directions =directions.reverse()
                if len(directions) != 0:
                    break
                            
        return directions


    def init_maze(self):
        print('Initialising Search')
        #Initialise robot search variables
        self.sectors = {} # dictionary of all sectors of the maze
        self.current_sector = {'x':0, 'y':0} #robot starts at 0,0
        #SEARCH CODE
        self.current_direction = "+y"
        return True


    def search_maze(self):
        search = self.init_maze()
        while search:
            current_sector_cp = '('+str(self.current_sector['x'])+', '+str(self.current_sector['y'])+')'
            print(current_sector_cp)
            if current_sector_cp in self.sectors:
                print('No previous sector')
                current_sector_vals = self.sectors[current_sector_cp]
            else:
                current_sector_vals = None
                print('Seen before')
            if not current_sector_vals:
                self.sectors[current_sector_cp] = {'walls': {}, 'entered':{}, 'complete': False}
                print('Searching')
                self.search_new_sector(current_sector_cp)
                print('Findished')
            else:
                print('Reviewing')
                search = self.search_old_sector(current_sector_cp)
        print(self.sectors)
        print('Terminated')
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
    ROBOT.search_maze()
    ROBOT.safe_exit()
