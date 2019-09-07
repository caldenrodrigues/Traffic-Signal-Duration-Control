import pygame
import json
from dateutil import parser
import datetime
import time as t

pygame.init()

display_width = pygame.display.Info().current_w
display_height = pygame.display.Info().current_h
#display_width = 1024
#display_height = 720
#gameDisplay = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
#Loading Images
carImg = pygame.image.load('Images/Car1.png')
carImgRev = pygame.image.load('Images/Car1_rev.png')
carImg = pygame.transform.scale(carImg, (20, 41))
carImgRev = pygame.transform.scale(carImgRev, (20, 41))

redImg = pygame.image.load('Images/red.png')
greenImg = pygame.image.load('Images/green.png')
#####################################################
data = []
COUNT_Lane1 = 0
COUNT_Lane2 = 0
LIGHTS_lane1_straight = 0 # 0 -> Red 1 -> Green
LIGHTS_lane2_straight = 1 # 0 -> Red 1 -> Green
second = "-1"
no_of_vehicles_per_second = 2
SIGNAL_Lane1_pos = (display_width * 0.55, display_height * 0.5)
SIGNAL_Lane2_pos = (display_width * 0.55, display_height * 0.35)

#EVENTS
EVENT_lane1_straight = pygame.USEREVENT + 1
pygame.time.set_timer(EVENT_lane1_straight, 10000)

EVENT_lane2_straight = pygame.USEREVENT + 2
pygame.time.set_timer(EVENT_lane2_straight, 10000)
#####################################################

#Load the data
with open('../Vehicle Detection/Yolo/output.txt') as f:
    data = json.load(f)["list"]
#print(data)
time = parser.parse(data[0]['time'])
final_time = parser.parse(data[-1]['time'])

def AddCar(x,y,img):
    #print(x,y,carImg)
    gameDisplay.blit(img, (x,y))

def AddCarsLane1(x):
    #print(x)
    inc_width = 30
    inc_height = 50
    initial_width = display_width * 0.45
    initial_height = display_height * 0.45
    width = initial_width
    height = initial_height
    for i in range(0,x):
        if(i%3 == 0):
            width = initial_width
            height += inc_height
        else:
            width += inc_width
        AddCar(width,height,carImg)

def AddCarsLane2(x):
    #print(x)
    inc_width = 30
    inc_height = -50
    initial_width = display_width * 0.5
    initial_height = display_height * 0.4
    width = initial_width
    height = initial_height
    for i in range(0,x):
        if(i%3 == 0):
            width = initial_width
            height += inc_height
        else:
            width += inc_width
        AddCar(width,height,carImgRev)

def render(Lane1, Lane2):
    gameDisplay.fill(white)
    gameDisplay.blit(Lane1[0], SIGNAL_Lane1_pos)
    gameDisplay.blit(Lane2[0], SIGNAL_Lane2_pos)
    AddCarsLane1(Lane1[1])
    AddCarsLane2(Lane2[1])

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == EVENT_lane1_straight:
            print("Switch in Lane1 Lights")
            if LIGHTS_lane1_straight == 1:
                LIGHTS_lane1_straight = 0
            else:
                LIGHTS_lane1_straight = 1
        if event.type == EVENT_lane2_straight:
            print("Switch in Lane2 Lights")
            if LIGHTS_lane2_straight == 1:
                LIGHTS_lane2_straight = 0
            else:
                LIGHTS_lane2_straight = 1

    current_second = datetime.datetime.now().strftime("%S")
    if(not current_second == second):
        second = current_second
        for i in data:
            current_time = parser.parse(i['time']).strftime("%H:%M:%S")
            if(current_time == time.strftime("%H:%M:%S") and i['direction'] == "in"):
                COUNT_Lane1+=1
                COUNT_Lane2+=1
        if time.strftime("%H:%M:%S") == final_time.strftime("%H:%M:%S"):
            crashed = True
        #Increment time by 1 second
        time = time + datetime.timedelta(seconds=1)

        #Checking if light status
        #Checking lane 1 Strainght
        if(not LIGHTS_lane1_straight):
            SIGNAL_Lane1 = redImg
        else:
            COUNT_Lane1-=no_of_vehicles_per_second
            if(COUNT_Lane1<0):
                COUNT_Lane1 = 0
            SIGNAL_Lane1 = greenImg
        if(not LIGHTS_lane2_straight):
            SIGNAL_Lane2 = redImg
        else:
            COUNT_Lane2-=no_of_vehicles_per_second
            if(COUNT_Lane2<0):
                COUNT_Lane2 = 0
            SIGNAL_Lane2 = greenImg
        render(Lane1 = [SIGNAL_Lane1,COUNT_Lane1], Lane2 = [SIGNAL_Lane2,COUNT_Lane2])
        '''
        if(not LIGHTS_lane1_straight):
            gameDisplay.fill(white)
            gameDisplay.blit(redImg, SIGNAL_Lane1)
            gameDisplay.blit(redImg, SIGNAL_Lane2)
            AddCarsLane1(COUNT_Lane1)
            AddCarsLane2(COUNT_Lane2)
        else:
            COUNT_Lane1-= no_of_vehicles_per_second
            if(COUNT_Lane1<0):
                COUNT_Lane1 = 0
            gameDisplay.fill(white)
            gameDisplay.blit(greenImg, SIGNAL_Lane1)
            gameDisplay.blit(redImg, SIGNAL_Lane2)
            AddCarsLane1(COUNT_Lane1)
            AddCarsLane2(COUNT_Lane2)
        #Checking lane 2 strainght
        if(not LIGHTS_lane2_straight):
            gameDisplay.fill(white)
            gameDisplay.blit(redImg, SIGNAL_Lane1)
            gameDisplay.blit(redImg, SIGNAL_Lane2)
            AddCarsLane1(COUNT_Lane1)
            AddCarsLane2(COUNT_Lane2)
        else:
            COUNT_Lane2-= no_of_vehicles_per_second
            if(COUNT_Lane2<0):
                COUNT_Lane2 = 0
            gameDisplay.fill(white)
            gameDisplay.blit(redImg, SIGNAL_Lane1)
            gameDisplay.blit(greenImg, SIGNAL_Lane2)
            AddCarsLane1(COUNT_Lane1)
            AddCarsLane2(COUNT_Lane2)
        '''
        #############################################
        pygame.display.update()
        clock.tick(60)

pygame.quit()
quit()
