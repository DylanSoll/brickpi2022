from interfaces import databaseinterface
import robot #robot is class that extends the brickpi class
import global_vars as GLOBALS #load global variables
import time
GLOBALS.DATABASE = databaseinterface.DatabaseInterface('databases/U3_SIA2_Rescue_Database-V1.db')


def log_movement(missionid, mov_type, time_init, power, movement_type, command_type, magnitude = False):
    if GLOBALS.DATABASE:
        GLOBALS.DATABASE.ModifyQuery('''INSERT INTO movement_log (missionid, type, time_init, magnitude, power,
         movement_type, command_type) VALUES (?, ?, ?, ?, ?, ?, ?)''', \
             (missionid, mov_type, time_init, magnitude, power, movement_type, command_type))
    return

def end_time_movement():
    if GLOBALS.DATABASE:
        GLOBALS.DATABASE('''UPDATE movement_log SET time_final = ? WHERE movementid = (SELECT movementid FROM movement_log 
        ORDER BY time_init DESC LIMIT 1)''', (time.time(),))
    return

def db_movement(movement):
    if GLOBALS.ROBOT:
        mov_type = movement['type']
        power = movement['power']
        duration = movement['duration']
        magnitude = movement['magnitude']
        movement_type = ['movement_type']
        #command_type = ['command_type']

        ###FORWARD BACKWARDS COMMANDS
        if mov_type == 'forward':
            if movement_type != 'distance':
                GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION)
        elif mov_type == 'forward-left':
            if movement_type != 'distance':
                GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION + -1 * 15)
        elif mov_type == 'forward-right':
            if movement_type != 'distance':
                GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION + 15)
        elif mov_type == 'backward-left':
            if movement_type != 'distance':
                GLOBALS.ROBOT.move_power_time(-1*power, duration, GLOBALS.DEVIATION + -1 * 15)
        elif mov_type == 'backward-right':
            if movement_type != 'distance':
                GLOBALS.ROBOT.move_power_time(-1*power, duration, GLOBALS.DEVIATION + 15)
        

        ### TURNING COMMANDS
        elif mov_type == 'right':
            if movement_type != 'degrees':
                GLOBALS.ROBOT.rotate_power_time(power, duration)
            elif movement_type == 'degrees':
                GLOBALS.ROBOT.rotate_power_degrees_IMU(power, magnitude)
        elif mov_type == 'left':
            if movement_type != 'degrees':
                GLOBALS.ROBOT.rotate_power_time(-power, duration)
            elif movement_type == 'degrees':
                GLOBALS.ROBOT.rotate_power_degrees_IMU(power, -magnitude)
    return

def reverse_path(missionid):
    if GLOBALS.DATABASE:
        movements = GLOBALS.DATABASE.ViewQuery('SELECT *, (time_final-time_init) AS duration FROM movement_log \
            WHERE missionid = ? ORDER BY time_init DESC', (missionid,))
        for i in range(len(movements)):
            movement = movements[i]
            if GLOBALS.ROBOT:
                mov_type = movement['type']
                power = movement['power']
                duration = movement['duration']
                magnitude = movement['magnitude']
                movement_type = ['movement_type']
                #command_type = ['command_type']

                ###FORWARD BACKWARDS COMMANDS
                if mov_type == 'forward':
                    if movement_type != 'distance':
                        GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION)
                elif mov_type == 'forward-left':
                    if movement_type != 'distance':
                        GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION + 15)
                elif mov_type == 'forward-right':
                    if movement_type != 'distance':
                        GLOBALS.ROBOT.move_power_time(power, duration, GLOBALS.DEVIATION + -1*15)
                elif mov_type == 'backward-left':
                    if movement_type != 'distance':
                        GLOBALS.ROBOT.move_power_time(-1*power, duration, GLOBALS.DEVIATION + 15)
                elif mov_type == 'backward-right':
                    if movement_type != 'distance':
                        GLOBALS.ROBOT.move_power_time(-1*power, duration, GLOBALS.DEVIATION + -1 * 15)
                

                ### TURNING COMMANDS
                elif mov_type == 'right':
                    if movement_type != 'degrees':
                        GLOBALS.ROBOT.rotate_power_time(-1*power, duration)
                    elif movement_type == 'degrees':
                        GLOBALS.ROBOT.rotate_power_degrees_IMU(-1*power, -1*magnitude)
                elif mov_type == 'left':
                    if movement_type != 'degrees':
                        GLOBALS.ROBOT.rotate_power_time(power, duration)
                    elif movement_type == 'degrees':
                        GLOBALS.ROBOT.rotate_power_degrees_IMU(power, magnitude)
    return

if __name__ == '__main__':
    reverse_path(1)
