#This is where your main robot code resides. It extendeds from the BrickPi Interface File
#It includes all the code inside brickpiinterface. The CurrentCommand and CurrentRoutine are important because they can keep track of robot functions and commands. Remember Flask is using Threading (e.g. more than once process which can confuse the robot)
from interfaces.brickpiinterface import *
import global_vars as GLOBALS
import logging
import numpy as np
from interfaces.jsonhelper import JSONHelper
from interfaces import databaseinterface
GLOBALS.DATABASE = databaseinterface.DatabaseInterface('databases/U3_SIA2_Rescue_Database-V1.db')

def upload_to_db(maze, missionid):
    if GLOBALS.DATABASE:
        sector_keys = maze.keys()
        mazeid_data =GLOBALS.DATABASE.ViewQuery('''SELECT mazeid FROM missions WHERE mazeid 
        IS NOT NULL ORDER BY mazeid DESC LIMIT 1''')
        if mazeid_data:
            mazeid_data = int(mazeid_data[0]['mazeid'])
            current_maze_id = mazeid_data + 1
        else:
            current_maze_id = 1 
        GLOBALS.DATABASE.ModifyQuery('UPDATE missions SET mazeid = ? WHERE missionid = ?;', (current_maze_id, missionid))
        print(GLOBALS.DATABASE.ViewQuery('SELECT * FROM missions WHERE missionid = ?', (missionid,)))
        for key in sector_keys:
            complete = maze[key]['complete']
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO sectors (mazeid, coordinate, complete) VALUES (?, ?, ?)',\
                (current_maze_id, key, complete))
            sectorid = GLOBALS.DATABASE.ViewQuery('SELECT sectorid FROM sectors ORDER BY sectorid DESC LIMIT 1')[0]['sectorid']
            for wall_key in maze[key]['walls'].keys():
                wall = maze[key]['walls'][wall_key]
                status = wall['status']
                victim = wall['victim']
                GLOBALS.DATABASE.ModifyQuery('''INSERT INTO walls (sectorid, direction, status, victim) VALUES (?, ?, ?, ?)''',\
                    (sectorid, wall_key, status, victim))
    return

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
            reverseDist = None
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
                if self.get_colour_sensor() != "White":
                    run = False
                    print(((BP.get_motor_encoder(BP.PORT_A))* np.pi * 5.6)/360)
                    print(((BP.get_motor_encoder(BP.PORT_D))* np.pi * 5.6)/360)
                    reverseDist = (((BP.get_motor_encoder(BP.PORT_A) + BP.get_motor_encoder(BP.PORT_B)))* np.pi * 5.6)/360
                if (self.get_ultra_sensor() < 20) and (self.get_ultra_sensor() not in [0,999]):
                    run = False
                    #reverseDist = (((BP.get_motor_encoder(BP.PORT_A) + BP.get_motor_encoder(BP.PORT_B))/2 )* np.pi * 5.6)/360
                
            time_final = time.time() #saves time final and duration
            print((((BP.get_motor_encoder(BP.PORT_A) + BP.get_motor_encoder(BP.PORT_B))/2 )* np.pi * 5.6)/360)

            duration = time_final - time_init
            return_val = {'distance':distanceCm, 'time_init': time_init, 'time_final': time_final, 'duration': duration, "reverseDist": reverseDist}
            #redefines return_Val as an array of distance, start and finish time, and duration
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all() #reset robot motors
        return return_val #returns return val


    def move_and_correct_move_dist(self, distanceCm, power = 30, speed=100, canTimeOut = False):
        vals = self.move_distance(distanceCm, power, speed, canTimeOut)
        if vals['reverseDist']:
            self.move_distance(-1*vals['reverseDist'])
            return True
        else:
            return False
    def right_degrees(self,angle,speed=100,power=100):   #power percent, degrees/second, degrees
        BP = self.BP
        degrees = angle*2 -2
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A)) # reset encoder A
            BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D)) # reset encoder D
            BP.set_motor_limits(BP.PORT_A, -1*power, speed)    # float motor D
            BP.set_motor_limits(BP.PORT_D, power, speed)          # optionally set a power limit (in percent) and a speed limit (in Degrees Per Second)
            while True:
                BP.set_motor_position(BP.PORT_D, degrees+5)    # set motor A's target position to the current position of motor D
                BP.set_motor_position(BP.PORT_A, -1*degrees-5)
                time.sleep(0.02)
                if BP.get_motor_encoder(BP.PORT_D) >= degrees or BP.get_motor_encoder(BP.PORT_A) <= -1*degrees:
                    break
        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            BP.reset_all()
        return
    
    
    
    

    #Create a function to search for victim

    
    def return_new_direction(self, old_direction):
        """Converts the old relative direction to new direction

        Args:
            old_direction (str): Current direction it faces

        Returns:
            str: new direction
        """        
        old_direction = old_direction.lower() #converts to lowercase
        mapping_direction = {'+y': '+x', '+x': 'y-', 'y-':'-x', '-x':'+y'} 
        #creates a dictionary for each direction and its next directions
        new_direction = mapping_direction[old_direction] #converts to new direction
        return new_direction #returns the value

    def face_direction_coord(self, wall_to_search, current_direction):
        """Rotates the robot to face the correct direction

        Args:
            wall_to_search (dict): Wall to search dict
            current_direction (str): Current facing of the robot

        Returns:
            str: Current direction robot is facing
        """        
        direction = wall_to_search.keys() #the first key in the dictionary is the direction
        for key in direction: #dict_keys() obj is quirky
            direction = key #loops through all keys, and the first one is the direction
            break #ends for loop
        target_heading = direction #use that to get the target direction
        while current_direction != target_heading: #while current direction
            current_direction = self.return_new_direction(current_direction) #updates direction
            self.right_degrees(90) #turns right 90 degrees
        return current_direction #returns current direction


    def update_sector_cp(self, direction):
        """Updates the robots coordinates

        Args:
            direction (str): Direction the robot is facing in

        Returns:
            str: direction the robot is facing in
        """        
        old_x = self.current_sector['x'] #retrieves x coordinate
        old_y = self.current_sector['y'] #retrieves y coordinate
        if 'x' in direction: #if robot moving in x direction
            new_y = old_y #y is unchanged
            if '-' in direction: #if direction is negative
                new_x = int(old_x) -1 #reduce x coord by 1
            elif '+' in direction: #if positive
                new_x = int(old_x) + 1 #increase x coord by 1
        elif 'y' in direction: #if robot moving in x direction
            new_x = old_x #x is unchanged
            if '-' in direction: #if direction is negative
                new_y = int(old_y) -1 #reduce y coord by 1
            elif '+' in direction: #if positive
                new_y = int(old_y) + 1 #increase y coord by 1
        self.current_sector['x'] = new_x #updates self.sector with new values
        self.current_sector['y'] = new_y
        return direction 


    #Create a routine that will effective search the maze and keep track of where the robot has been.
    def search_new_sector(self, current_sector_cp):
        walls = {} #creates a blank list for all the walls
        wall_to_search = None #the wall that is to be searched first
        entered = False
        for wall in range(4): #up to 4 walls per box
            ##for each wall

            ####Wall definitions
            status = False #predefines status as False
            victim = False #predefines victim as false
            explored = False #predefines explored as false

            for _ in range(5): #runs through 5 times too account for void values
                print(self.get_ultra_sensor())
                if self.get_ultra_sensor() < 25 and self.get_ultra_sensor() not in [0,999]: #there is a wall
                    status = True #there is a wall
                    print('Wall:' + str(status))
                    break #exits for loop
                elif self.get_ultra_sensor() not in [0,999]:
                    break #exits for loop if valid 


            
            #if there is a wall, and how to check for victims
            if status == True: #if wall
                if GLOBALS.CAMERA: #make sure the camera is working
                    h = GLOBALS.CAMERA.find_h(GLOBALS.CAMERA.data) #call find_h code
                    for _ in h: #runs through all the victims
                        self.spin_medium_motor(1000) #fires the package 
                        victim = 'H'
                    else: #U can sometimes be detected in H, so if no H, check for 'U'
                        u = GLOBALS.CAMERA.find_u(GLOBALS.CAMERA.data) #checks for a 'U'
                        for _ in u: #runs through all unharmed victims
                            victim = 'U'
                            if GLOBALS.SOUND: #checks for a speaker, and reassures victim
                                GLOBALS.SOUND.say('Medical professionals will be with you shortly')


            elif status == False:#must be no wall
                if wall_to_search == None: #checks to see if a first move has been planned
                    if wall == 2 and current_sector_cp != "(0, 0)": 
                        #if this has an ID of 2, it must be the entry point
                        #however if the sector is 0,0, it has no entry
                        explored = False #the wall is not to be explored
                    else:
                        explored = True #this is the wall to explore
                        

            temp_wall = {'status':status, 'victim': victim, 'explored': explored}
            #creates a dict of all the relevant details


            if explored: #checks to see if the wall can be explored
                wall_to_search = {self.current_direction: temp_wall} #defines wall to search as this wall
            if wall == 2 and current_sector_cp != "(0, 0)": 
                entered = {self.current_direction: temp_wall} #saves the details 
            elif current_sector_cp == "(0, 0)":
                entered = False #if it is the origin, it wouldn't have entered

            walls[self.current_direction] = temp_wall #adds to dictionary of walls
            self.right_degrees(90) #turns right 90 degrees
            self.current_direction = self.return_new_direction(self.current_direction) 
            #updates direction the robot is facing
        
        complete_status = False
        if wall_to_search != None: #if there is a wall to search
            self.current_direction = self.face_direction_coord(wall_to_search, self.current_direction)
            #change direction to face the required direction
            self.current_direction = self.update_sector_cp(self.current_direction) #updates the sector
            self.move_distance(40)
            #####UPDATE CODE TO DEAL WITH NO FLOOR
        else:
            complete_status = True #the sector must be done with, can ignore
            if entered != False: # find the entrance, and leave
                self.current_direction = self.face_direction_coord(entered, self.current_direction)
                #same as move to new sector
                self.current_direction = self.update_sector_cp(self.current_direction)
                self.move_distance(40)

        self.sectors[current_sector_cp] = {'walls': {}, 'entered':{}, 'complete': complete_status}
        #creates a default value to avoid key errors
        #while python collections modules could be used (defualt dictionary) but is not necessary
        self.sectors[current_sector_cp]['walls'] = walls #inserts walls into major sectors dictionary
        self.sectors[current_sector_cp]['entered'] = entered
        #saves the wall entered from
        return

    def search_old_sector(self, current_sector_cp):
        #definitions of variables
        cont_search = True 
        possible_movement = None

        #retrieves details from sectors dictionary
        walls = self.sectors[current_sector_cp]['walls']
        entered_from = self.sectors[current_sector_cp]['entered']
        
        #processes entered from direction
        if entered_from:
            entered_direction_dict_keys = entered_from.keys()
            for key in entered_direction_dict_keys: #creates a dict_keys, and retrieves data
                entered_direction = key #saves the key and exits
                break
        else:
            entered_direction = False #otherwise there is no entrance

        
        wall_keys = walls.keys() #retrieves all the walls
        for key in wall_keys: #for each wall
            wall = walls[key] #retrieves the wall details
            print(wall['status'], wall['explored'], "ED"+str(entered_direction), key)
            #if there is no wall, it is unexplored, and not the entrance direction
            if wall['status'] == False and wall['explored'] == False and key != entered_direction:
                possible_movement = key #labels it as the next movement
                self.sectors[current_sector_cp]['walls'][key]['explored'] = True
                #updates as explored

                #####UPDATE MOVEMENT CODE
                self.current_direction = self.face_direction_coord({key:wall}, self.current_direction)
                self.move_distance(40)
                self.current_direction = self.update_sector_cp(self.current_direction)
                break

        #If no possible movement    
        if possible_movement == None:
            self.sectors[current_sector_cp]['complete'] = True #update sector status
            if current_sector_cp == '(0, 0)':
                cont_search = False #stop searching
            else:
                #head to next square and update sector
                self.current_direction = self.face_direction_coord(entered_from, self.current_direction)
                self.move_distance(40)
                self.current_direction = self.update_sector_cp(self.current_direction)
        return cont_search

    def scan_maze_logs(self, sectors):
        directions = []
        
        sector_coords = sectors.keys()
        for coord in sector_coords:
            sector = sectors[coord]
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
                            



        


    def search_maze(self):
        print('Initialising Search')
        #Initialise robot search variables
        self.sectors = {} # dictionary of all sectors of the maze
        self.current_sector = {'x':0, 'y':0} #robot starts at 0,0
        #SEARCH CODE
        self.current_direction = "+y"
        search = True #start searching
        while search: 
            current_sector_cp = '('+str(self.current_sector['x'])+', '+str(self.current_sector['y'])+')'
            #convert dict values to coordinate string format
            print(current_sector_cp)
            if current_sector_cp in self.sectors: #if the square has been reached before
                current_sector_vals = self.sectors[current_sector_cp] #potentially obselete
                print('Reviewing sector:', current_sector_cp)
                search = self.search_old_sector(current_sector_cp) #search the old sector
            else:
                self.sectors[current_sector_cp] = {'walls': {}, 'entered':{}, 'complete': False} #created to avoid keyerrors
                print('Searching new sector:', current_sector_cp) 
                self.search_new_sector(current_sector_cp)#search the new sector discovered
        print(self.sectors)
        print('Terminated')
        ##ON TERMINATION
        if GLOBALS.SOUND:
            GLOBALS.SOUND.say('Search Complete')
        
        if GLOBALS.DATABASE and GLOBALS.MISSIONID:
            upload_to_db(self.sectors, GLOBALS.MISSIONID) #saves to database   
              
        ##LOG EVERYTHING TO DATABASE
        return 





# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    ROBOT = Robot()
