from turtle import *
screen_size = 600 

setup(screen_size, screen_size)
title("Sector Drawing Test Zone")
bgcolor("blue")
shape("turtle")
speed('fastest')
colormode(255)
pencolor((255,255,255))
def draw_square(size, pen_colour = False, fill_colour = False):
    if pen_colour:
        pencolor(pen_colour)
    if fill_colour:
        fillcolor(fill_colour)
        begin_fill()
    for i in range(4):
        forward(size)
        right(90)
    if fill_colour:
        fillcolor(fill_colour)
        end_fill()
    return

class Sector():
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        return
    
    def go_to(self, x, y, heading = 0):
        penup()
        goto(x, y)
        pendown()
        setheading(heading)
    


    def draw_victim(self, victim_type, x,y):
        pensize(1)
        if victim_type == 'harmed':
            self.go_to(x, y)
            draw_square(15, (255,90,90), (255,90,90))
            self.go_to(x +2, y - 20)
            pencolor((0,0,0))
            write('H', font=('Calibri', 15, 'italic'))
        if victim_type == 'unharmed':
            self.go_to(x, y)
            draw_square(15, (90,255,90), (90,255,90))
            self.go_to(x +2, y - 20)
            pencolor((0,0,0))
            write('U', font=('Calibri', 15, 'italic'))
            

    def draw_wall(self, wall_type,x,y, heading = 0):
        setheading(heading)
        pencolor((255,255,255))
        if wall_type == False:
            pensize(1)
            forward(30)

        else:
            pendown()
            pensize(3)
            forward(30)
        x_ret, y_ret = pos()
        if wall_type == 'harmed' or wall_type =='unharmed':
            if heading == 0:
                h_y = y + 7.5
                h_x = x + 7.5
            elif heading == 90:
                h_y = y + 22.5
                h_x = x - 7.5
            elif heading == 180:
                h_y = y + 7.5
                h_x = x - 22.5
            elif heading == 270:
                h_y = y - 7.5
                h_x = x - 7.5
            if wall_type == 'harmed':
                self.draw_victim('harmed', h_x,h_y)
            elif wall_type == 'unharmed':
                self.draw_victim('unharmed', h_x,h_y)
        self.go_to(x_ret, y_ret, heading)
        return


    def draw_sector(self,walls, sector):
        self.go_to(self.start_x, self.start_y)
        for i in range(4):
            current_data = walls[i]
            x, y = pos()
            self.draw_wall(current_data, x, y, 90*i)
        self.go_to(x+5, y-25)
        pencolor((255,255,255))
        write(sector)
        return
#sector = Sector(0,0)
#sector.draw_victim('h', 10, 10)

def sector_creator(cp_x, cp_y, current_data):
    x = cp_x * 30; y = cp_y * 30
    sector = Sector(x, y)
    sector.draw_sector(current_data, str(cp_x)+","+str(cp_y))
    return


#ORDER IS -Y, X+, Y+, X-
current_data = [True, False, 'unharmed', True]
sector_creator(-1, -1, current_data)
current_data = [True, True, False, False]
sector_creator(0, -1, current_data)
current_data = [False, 'harmed',True, False]
sector_creator(0, 0, current_data)
current_data = [True, False, True, True]
sector_creator(-1, 0, current_data)
hideturtle()
done()