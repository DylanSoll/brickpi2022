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



    #Create a function to move time and power which will stop if colour is detected or wall has been found
    
    
    

    #Create a function to search for victim
    

    
    
    
    #Create a routine that will effective search the maze and keep track of where the robot has been.






# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logging.basicConfig(filename='logs/robot.log', level=logging.INFO)
    ROBOT = Robot(timelimit=10)  #10 second timelimit before
    ROBOT.configure_sensors() #This takes 4 seconds
    #ROBOT.rotate_power_degrees_IMU(20,-90)
    start = time.time()
    limit = start + 10
    #print(ROBOT.get_linear_acceleration_IMU()[1])
    ROBOT.move_distance(-30)
    while (time.time() < limit):
        compass = ROBOT.get_compass_IMU()
        print(compass)
    sensordict = ROBOT.get_all_sensors()
    ROBOT.safe_exit()
