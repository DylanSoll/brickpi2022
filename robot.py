#This is where your main robot code resides. It extendeds from the BrickPi Interface File
#It includes all the code inside brickpiinterface. The CurrentCommand and CurrentRoutine are important because they can keep track of robot functions and commands. Remember Flask is using Threading (e.g. more than once process which can confuse the robot)
from interfaces.brickpiinterface import *
import global_vars as GLOBALS
import logging

class Robot(BrickPiInterface):
    
    def __init__(self, timelimit=10, logger=logging.getLogger()):
        super().__init__(timelimit, logger)
        self.CurrentCommand = "stop" #use this to stop or start functions
        self.CurrentRoutine = "stop" #use this stop or start routines
        return
        
    def move_power_distance(self, power, distance):
        self.interrupt_previous_command()
        bp = self.BP
        if (self.config['imu'] >= SensorStatus.DISABLED):
            return
        self.interrupt_previous_command()
        self.CurrentCommand = "move_power_distance"
        self.reconfig_IMU()
        data = {'rotated':0,'elapsed':0}

        if distance < 0:
            distance = -1*distance
            if power > 0:
                power = power * -1
        
        starttime = time.time(); timelimit = starttime + self.timelimit
        #start motors 
        bp.set_motor_power(self.rightmotor, power)
        bp.set_motor_power(self.leftmotor, -power)
        total_cm = 0
        while (total_cm < distance) and (self.CurrentCommand == "move_power_distance") and (time.time() < timelimit) and (self.config['imu'] < SensorStatus.DISABLED):
            lastrun = time.time()
            accel = self.get_linear_acceleration_IMU()
            t = time.time() - lastrun
            distance_tra =  accel*t**2 + 1/2*accel*t**2
            total_cm += distance_tra
            self.log(total_cm)
        self.stop_all()

        data['action'] = self.CurrentCommand
        data['elapsed'] = time.time() - starttime
        data['dinstance'] = total_cm
        return data
    #Create a function to move time and power which will stop if colour is detected or wall has been found
    
    
    

    #Create a function to search for victim
    

    
    
    
    #Create a routine that will effective search the maze and keep track of where the robot has been.






# Only execute if this is the main file, good for testing code
if __name__ == '__main__':
    logging.basicConfig(filename='logs/robot.log', level=logging.INFO)
    ROBOT = Robot(timelimit=10)  #10 second timelimit before
    bp = ROBOT.BP
    ROBOT.configure_sensors() #This takes 4 seconds
    ROBOT.rotate_power_degrees_IMU(20,-90)
    start = time.time()
    limit = start + 10
    while (time.time() < limit):
        compass = ROBOT.get_compass_IMU()
        print(compass)
    sensordict = ROBOT.get_all_sensors()
    ROBOT.safe_exit()
