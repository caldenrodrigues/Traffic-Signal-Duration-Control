import pygame
import json
from dateutil import parser
import datetime
import time as t

pygame.init()

display_width = 1024
display_height = 720

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('Images/Car1.png')
carImg = pygame.transform.scale(carImg, (20, 41))
redImg = pygame.image.load('Images/red.png')
greenImg = pygame.image.load('Images/green.png')
data = []
no_of_cars = 0
light_on = 0 # 0 -> Red 1 -> Green
second = "-1"
no_of_vehicles_per_second = 3

EVENT_lane1_straight = pygame.USEREVENT
LIGHTS_EVENT = pygame.USEREVENT   # Event code for Lights change
pygame.time.set_timer(LIGHTS_EVENT, 20000)

#Load the data
with open('../Vehicle Detection/Yolo/output.txt') as f:
    data = json.load(f)["list"]
#print(data)
time = parser.parse(data[0]['time'])
final_time = parser.parse(data[-1]['time'])

def AddCar(x,y):
    gameDisplay.blit(carImg, (x,y))

def AddCars(x):
    print(x)
    inc_width = 30
    inc_height = 50
    initial_width = 0
    initial_height = 0
    width = initial_width
    height = initial_height
    for i in range(0,x):
        if(i%3 == 0):
            width = initial_width
            height += inc_height
        else:
            width += inc_width
        AddCar(width,height)

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == LIGHTS_EVENT:
            print("lights")
            if light_on == 1:
                light_on = 0
            else:
                light_on = 1

    current_second = datetime.datetime.now().strftime("%S")
    if(not current_second == second):
        second = current_second
        for i in data:
            current_time = parser.parse(i['time']).strftime("%H:%M:%S")
            if current_time == time.strftime("%H:%M:%S"):
                no_of_cars+=1
                # gameDisplay.fill(white)
                # AddCars(no_of_cars)
        if time.strftime("%H:%M:%S") == final_time.strftime("%H:%M:%S"):
            crashed = True
        #Increment time by 1 second
        time = time + datetime.timedelta(seconds=1)

        if(not light_on):
            gameDisplay.fill(white)
            gameDisplay.blit(redImg, (100,100))
            AddCars(no_of_cars)
        else:
            no_of_cars-= no_of_vehicles_per_second
            if(no_of_cars<0):
                no_of_cars = 0
            gameDisplay.fill(white)
            gameDisplay.blit(greenImg, (100,100))
            AddCars(no_of_cars)

        pygame.display.update()
        clock.tick(60)

pygame.quit()
quit()
