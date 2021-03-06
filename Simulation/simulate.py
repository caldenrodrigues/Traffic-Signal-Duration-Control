import pygame
import json
from dateutil import parser
import datetime
import time as t
import random
import datetime
import math
pygame.init()

display_width = pygame.display.Info().current_w
display_height = pygame.display.Info().current_h
#display_width = 1024
#display_height = 720
#gameDisplay = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Traffic Signal Duration Control')

black = (0, 0, 0)
white = (255, 255, 255)
speed = 1
clock = pygame.time.Clock()
crashed = False

# Loading Images
# Cars Straight
carStraightNorth = pygame.image.load(
    'Images/CarStraightNorth.png').convert_alpha()
carStraightSouth = pygame.image.load(
    'Images/CarStraightSouth.png').convert_alpha()
carStraightEast = pygame.image.load(
    'Images/CarStraightEast.png').convert_alpha()

carStraightNorth = pygame.transform.scale(carStraightNorth, (20, 41))
carStraightSouth = pygame.transform.scale(carStraightSouth, (20, 41))
carStraightEast = pygame.transform.scale(carStraightEast, (41, 20))

# Cars Left
carLeftNorth = pygame.image.load('Images/CarLeftNorth.png').convert_alpha()
carLeftSouth = pygame.image.load('Images/CarLeftSouth.png').convert_alpha()
carLeftEast = pygame.image.load('Images/CarLeftEast.png').convert_alpha()

carLeftNorth = pygame.transform.scale(carLeftNorth, (20, 41))
carLeftSouth = pygame.transform.scale(carLeftSouth, (20, 41))
carLeftEast = pygame.transform.scale(carLeftEast, (41, 20))

# Cars Right
carRightNorth = pygame.image.load('Images/CarRightNorth.png').convert_alpha()
carRightSouth = pygame.image.load('Images/CarRightSouth.png').convert_alpha()
carRightEast = pygame.image.load('Images/CarRightEast.png').convert_alpha()

carRightNorth = pygame.transform.scale(carRightNorth, (20, 41))
carRightSouth = pygame.transform.scale(carRightSouth, (20, 41))
carRightEast = pygame.transform.scale(carRightEast, (41, 20))

# Trucks
truckStraightNorth = pygame.image.load(
    'Images/TruckStraight.png').convert_alpha()
truckStraightNorth = pygame.transform.scale(truckStraightNorth, (22, 46))
truckStraightSouth = pygame.transform.rotate(truckStraightNorth, 180)
truckStraightEast = pygame.transform.rotate(truckStraightNorth, 270)

truckLeftNorth = pygame.image.load('Images/TruckLeft.png').convert_alpha()
truckLeftNorth = pygame.transform.scale(truckLeftNorth, (22, 46))
truckLeftSouth = pygame.transform.rotate(truckLeftNorth, 180)
truckLeftEast = pygame.transform.rotate(truckLeftNorth, 270)

truckRightNorth = pygame.image.load('Images/TruckRight.png').convert_alpha()
truckRightNorth = pygame.transform.scale(truckRightNorth, (22, 46))
truckRightSouth = pygame.transform.rotate(truckRightNorth, 180)
truckRightEast = pygame.transform.rotate(truckRightNorth, 270)

# Divider
dividerRoad = pygame.image.load('Images/Divider.png').convert_alpha()
dividerRoad = pygame.transform.rotate(dividerRoad, 90)
dividerRoad = pygame.transform.scale(dividerRoad, (20, 20))

# Grass
grass = pygame.image.load('Images/grass.jpg').convert_alpha()
grass = pygame.transform.scale(grass, (20, 20))

# Signals
signal1 = pygame.image.load('Images/Signal1.png').convert_alpha()
signalRed = pygame.image.load('Images/Red.png').convert_alpha()
signal1Straight = pygame.image.load(
    'Images/Signal1Straight.png').convert_alpha()
signal2 = pygame.image.load('Images/Signal2.png').convert_alpha()
signal2Red = pygame.image.load('Images/Signal2Red.png').convert_alpha()
signal3 = pygame.image.load('Images/Signal3.png').convert_alpha()
signal3Red = pygame.image.load('Images/Signal3Red.png').convert_alpha()

signalLane1 = signalRed
signalLane2 = signal2Red
signalLane3 = signal3Red

#Counter font
counterFont = pygame.font.Font("Images/Poppins-Light.ttf", 18);

#####################################################

# Initialization
# Unique Id given to every car
id = 0
# Data Lanes
DataLane1 = []
DataLane2 = []
DataLane3 = []
# List Lanes
ListLane1 = []
ListLane2 = []
ListLane3 = []
ListLane4 = []
ListLane4 = []
ListLane5 = []
ListLane6 = []
# Endpoints for each lane
EndPoint_Lane1 = [display_width * 0.45, display_height * 0.5]
EndPoint_Lane2 = [display_width*0.4, display_height * 0.45]
EndPoint_Lane3 = [display_width * 0.45, 0]
EndPoint_Lane4 = [display_width * 0.45, display_height * 0.35]
EndPoint_Lane5 = [display_width, display_height * 0.45]
EndPoint_Lane6 = [display_width, display_height]
# variable which determines which signal is on
signalOn = 0
# Which sub lane to initiate the car in
CurrentPoint_Lane1 = 0
CurrentPoint_Lane2 = 0
CurrentPoint_Lane3 = 0
CurrentPoint_Lane4 = 0
CurrentPoint_Lane5 = 0
CurrentPoint_Lane6 = 0
# Used to compare with current second
second = "-1"
# check
no_of_vehicles_per_second = 3
signalPositionLane1 = (display_width * 0.5, display_height * 0.5)
signalPositionLane2 = (display_width * 0.38, display_height * 0.35)
signalPositionLane3 = (display_width * 0.5, display_height * 0.3)

#font = pygame.font.SysFont('Consolas', 30)

# EVENTS
EVENT = pygame.USEREVENT + 1
EVENT_SECOND = pygame.USEREVENT + 2
pygame.time.set_timer(EVENT, 10000)
pygame.time.set_timer(EVENT_SECOND, 1000)
#####################################################

# Load the data
# with open('../Vehicle Detection/Yolo/output_lane3.txt') as f:
#     data = json.load(f)["list"]
with open('../Vehicle Detection/RealTIme/simulationDataLane1.txt') as f:
    DataLane1 = json.load(f)["list"]
# for i in range(0, 77):
#     temp = DataLane1[i]
#     tempTime =  datetime.datetime.strptime(temp["time"], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(seconds=90)
#     temp["time"] = tempTime.strftime("%Y-%m-%d %H:%M:%S.%f")
#     DataLane2.append(temp)
# for i in range(0, 77):
#     temp = DataLane1[i]
#     tempTime =  datetime.datetime.strptime(temp["time"], '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(seconds=180)
#     temp["time"] = tempTime.strftime("%Y-%m-%d %H:%M:%S.%f")
    # DataLane3.append(temp)
with open('../Vehicle Detection/RealTIme/simulationDataLane2.txt') as f:
    DataLane2 = json.load(f)["list"]
with open('../Vehicle Detection/RealTIme/simulationDataLane3.txt') as f:
    DataLane3 = json.load(f)["list"]
# print(data)
time = parser.parse(DataLane1[0]['time'])
final_time = parser.parse(DataLane1[-1]['time'])


percentageData = []
with open('../Vehicle Detection/RealTIme/output.txt') as f:
    outputData = json.load(f)["list"]


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


outputData = list(chunks(outputData, 1350))
percentageData = []
for i in range(0, len(outputData)-1):
    percentageData.append(
        (sum(float(item['Percentage']) for item in outputData[i])/1350)/100)
print("Normalized Density:")
print(percentageData)

speedData = []
for i in range(0, len(outputData)-1):
    speedData.append(sum(float(item['Speed']) for item in outputData[i])/1350)
for i in range(0, len(speedData)):
    speedData[i] = speedData[i] / max(speedData)
print("Normalized Speed:")
print(speedData)

laneWeight = []
a = 1
b = 1
for i in range(0, len(percentageData)):
    laneWeight.append((a * percentageData[i] + b * speedData[i]) / (a+b))
print("Lane Weights:")
print(laneWeight)

laneTime = []
for i in range(0, len(laneWeight)):
    index1 = i
    index2 = (i+1) % len(laneWeight)
    index3 = (i+2) % len(laneWeight)
    s = laneWeight[index1] + laneWeight[index2] + laneWeight[index3]
    time1 = round((laneWeight[index1] / s ) * 90)
    time2 = round((laneWeight[index2] / s ) * 90)
    time3 = round((laneWeight[index3] / s ) * 90)
    laneTime.append([time1, time2, time3])
print("Lane Time:")
print(laneTime)


def AddCar(x, y, img):
    # print(x,y,carImg)
    gameDisplay.blit(img, (x, y))


def AddCarsLane(l, carStraight, carLeft, carRight, truckStraight, truckLeft, truckRight):
    # print(l)
    for i in l:
        if(i["type"] == "car"):
            if(i["direction"] == "Straight"):
                AddCar(i["CurrentPoint"][0], i["CurrentPoint"][1], carStraight)
            elif i["direction"] == "Left":
                AddCar(i["CurrentPoint"][0], i["CurrentPoint"][1], carLeft)
            else:
                AddCar(i["CurrentPoint"][0], i["CurrentPoint"][1], carRight)

        elif(i["type"] == "truck"):
            if(i["direction"] == "Straight"):
                AddCar(i["CurrentPoint"][0],
                       i["CurrentPoint"][1], truckStraight)
            elif i["direction"] == "Left":
                AddCar(i["CurrentPoint"][0], i["CurrentPoint"][1], truckLeft)
            else:
                AddCar(i["CurrentPoint"][0], i["CurrentPoint"][1], truckRight)

# Some point variables I didnt know where else I should have put.
road1start = EndPoint_Lane1[0]-30
road1width = 250
road2start = EndPoint_Lane2[1]-80
road2height = 130


# Initialize background

#   Grass
for y in range(0, display_height, 20):
    for x in range(0, display_width, 20):
        gameDisplay.blit(grass, (x, y))

# Index
indexStart = road1start-350
indexTop = road2start+250

pygame.draw.rect(gameDisplay, (255,255,255), (indexStart, indexTop, 250, 130))
pygame.draw.rect(gameDisplay, (0,0,0), (indexStart, indexTop, 250, 130), 4)
gameDisplay.blit(counterFont.render("INDEX", True, (20,20,20)), (indexStart+100, indexTop+10))
gameDisplay.blit(carStraightEast, (indexStart+10, indexTop+40))
gameDisplay.blit(truckStraightEast, (indexStart+60, indexTop+40))
gameDisplay.blit(counterFont.render("Goes Straight", True, (20,20,20)), (indexStart+120, indexTop+40))
gameDisplay.blit(carLeftEast, (indexStart+10, indexTop+70))
gameDisplay.blit(truckLeftEast, (indexStart+60, indexTop+70))
gameDisplay.blit(counterFont.render("Turns Left", True, (20,20,20)), (indexStart+120, indexTop+70))
gameDisplay.blit(carRightEast, (indexStart+10, indexTop+100))
gameDisplay.blit(truckRightEast, (indexStart+60, indexTop+100))
gameDisplay.blit(counterFont.render("Turns Right", True, (20,20,20)), (indexStart+120, indexTop+100))

########

def render():
    #gameDisplay.fill((255, 255, 255))
    # Road
    pygame.draw.rect(gameDisplay, (50, 50, 50),
                     (road1start, 0, road1width, display_height), 0)
    pygame.draw.rect(gameDisplay, (255, 255, 255),
                     (road1start, 0, road1width, display_height), 4)
    pygame.draw.rect(gameDisplay, (50, 50, 50),
                     (0, road2start, display_width, road2height), 0)
    pygame.draw.rect(gameDisplay, (255, 255, 255),
                     (0, road2start, display_width, road2height), 4)
    pygame.draw.rect(gameDisplay, (255, 255, 255),
                     (road1start, road2start, road1width, road2height), 4)

    # Divider
    for y in range(0, int(signalPositionLane3[1]), 20):
        gameDisplay.blit(dividerRoad, (signalPositionLane3[0]+5, y))

    for y in range(int(signalPositionLane1[1]), display_height, 20):
        gameDisplay.blit(dividerRoad, (signalPositionLane3[0]+5, y))

    # Traffic Light
    gameDisplay.blit(signalLane1, signalPositionLane1)
    gameDisplay.blit(signalLane2, signalPositionLane2)
    gameDisplay.blit(signalLane3, signalPositionLane3)

    # Add vehicles
    AddCarsLane(ListLane1, carStraightNorth, carLeftNorth, carRightNorth,
                truckStraightNorth, truckLeftNorth, truckRightNorth)
    AddCarsLane(ListLane3, carStraightNorth, carLeftNorth, carRightNorth,
                truckStraightNorth, truckLeftNorth, truckRightNorth)
    AddCarsLane(ListLane5, carStraightEast, carLeftEast, carRightEast,
                truckStraightEast, truckLeftEast, truckRightEast)
    AddCarsLane(ListLane2, carStraightEast, carLeftEast, carRightEast,
                truckStraightEast, truckLeftEast, truckRightEast)
    AddCarsLane(ListLane6, carStraightSouth, carLeftSouth, carRightSouth,
                truckStraightSouth, truckLeftSouth, truckRightSouth)
    AddCarsLane(ListLane4, carStraightSouth, carLeftSouth, carRightSouth,
                truckStraightSouth, truckLeftSouth, truckRightSouth)

    # Counter
    counter1x = signalPositionLane1[0]
    counter1y = signalPositionLane1[1] + 80

    counter2x = signalPositionLane2[0] - 30
    counter2y = signalPositionLane2[1] - 1

    counter3x = signalPositionLane3[0]
    counter3y = signalPositionLane3[1] - 30
    
    pygame.draw.rect(gameDisplay, (0, 0, 0), (counter1x, counter1y, 30, 30))
    pygame.draw.rect(gameDisplay, (255, 215, 0), (counter1x, counter1y, 30, 30), 1)
    gameDisplay.blit(counterFont.render(str(TimeSignal1),
                                 True, (0, 230, 0)), (counter1x+3, counter1y+2))
    
    pygame.draw.rect(gameDisplay, (0, 0, 0), (counter2x, counter2y, 30, 30))
    pygame.draw.rect(gameDisplay, (255, 215, 0), (counter2x, counter2y, 30, 30), 1)
    gameDisplay.blit(counterFont.render(str(TimeSignal2),
                                 True, (0, 230, 0)), (counter2x+3, counter2y+2))

    pygame.draw.rect(gameDisplay, (0, 0, 0), (counter3x, counter3y, 30, 30))
    pygame.draw.rect(gameDisplay, (255, 215, 0), (counter3x, counter3y, 30, 30), 1)
    gameDisplay.blit(counterFont.render(str(TimeSignal3),
                                 True, (0,230,0)), (counter3x+3, counter3y+2))


def movePosition():
    for i in ListLane1:
        if(i["CurrentPoint"][1] > i["EndPoint"][1]):
            min = 999999
            diff = 999999
            for j in ListLane1:
                diff = i["CurrentPoint"][1] - j["CurrentPoint"][1]
                if(diff > 0 and diff < min and i["CurrentPoint"][0] == j["CurrentPoint"][0]):
                    min = diff
            if(min > 50):
                i["CurrentPoint"] = [i["CurrentPoint"]
                                     [0], i["CurrentPoint"][1]-speed]

    for i in ListLane2:
        if(i["CurrentPoint"][0] < i["EndPoint"][0]):
            min = 999999
            diff = 999999
            for j in ListLane2:
                diff = j["CurrentPoint"][0]-i["CurrentPoint"][0]
                if(diff > 0 and diff < min and i["CurrentPoint"][1] == j["CurrentPoint"][1]):
                    min = diff
            if(min > 50):
                i["CurrentPoint"] = [i["CurrentPoint"]
                                     [0]+speed, i["CurrentPoint"][1]]

    for i in ListLane3:
        min = 999999
        diff = 999999
        for j in ListLane3:
            diff = i["CurrentPoint"][1] - j["CurrentPoint"][1]
            if(diff > 0 and diff < min and i["CurrentPoint"][0] == j["CurrentPoint"][0]):
                min = diff
        if(min > 50):
            i["CurrentPoint"] = [i["CurrentPoint"][0], i["CurrentPoint"][1]-speed]

    for i in ListLane5:
        min = 999999
        diff = 999999
        for j in ListLane5:
            diff = i["CurrentPoint"][1] - j["CurrentPoint"][1]
            if(diff > 0 and diff < min and i["CurrentPoint"][0] == j["CurrentPoint"][0]):
                min = diff
        if(min > 50):
            i["CurrentPoint"] = [i["CurrentPoint"][0]+speed, i["CurrentPoint"][1]]

    for i in ListLane6:
        min = 999999
        diff = 999999
        for j in ListLane6:
            diff = i["CurrentPoint"][0] - j["CurrentPoint"][0]
            if(diff > 0 and diff < min and i["CurrentPoint"][1] == j["CurrentPoint"][1]):
                min = diff
        if(min > 50):
            i["CurrentPoint"] = [i["CurrentPoint"][0], i["CurrentPoint"][1]+speed]

    for i in ListLane4:
        if(i["CurrentPoint"][1] < i["EndPoint"][1]):
            min = 999999
            diff = 999999
            for j in ListLane4:
                diff = j["CurrentPoint"][1]-i["CurrentPoint"][1]
                if(diff > 0 and diff < min and i["CurrentPoint"][0] == j["CurrentPoint"][0]):
                    min = diff
            if(min > 50):
                i["CurrentPoint"] = [i["CurrentPoint"]
                                     [0], i["CurrentPoint"][1]+speed]


def getCurrentPointLane1():
    global CurrentPoint_Lane1
    if(CurrentPoint_Lane1 == 0):
        CurrentPoint_Lane1 = 1
        return [display_width * 0.45, display_height]
    elif(CurrentPoint_Lane1 == 1):
        CurrentPoint_Lane1 = 2
        return [display_width * 0.45 + 30, display_height]
    else:
        CurrentPoint_Lane1 = 0
        return [display_width * 0.45 + 60, display_height]


def getCurrentPointLane2():
    global CurrentPoint_Lane2
    if(CurrentPoint_Lane2 == 0):
        CurrentPoint_Lane2 = 1
        return [0, display_height*0.4]
    elif(CurrentPoint_Lane2 == 1):
        CurrentPoint_Lane2 = 2
        return [0, display_height*0.4+30]
    else:
        CurrentPoint_Lane2 = 0
        return [0, display_height*0.4+60]


def getCurrentPointLane3():
    global CurrentPoint_Lane3
    if(CurrentPoint_Lane3 == 0):
        CurrentPoint_Lane3 = 1
        return [display_width * 0.45, display_height*0.35]
    elif(CurrentPoint_Lane3 == 1):
        CurrentPoint_Lane3 = 2
        return [display_width * 0.45 + 30, display_height*0.35]
    else:
        CurrentPoint_Lane3 = 0
        return [display_width * 0.45 + 60, display_height*0.35]


def getCurrentPointLane5():
    global CurrentPoint_Lane5
    if(CurrentPoint_Lane5 == 0):
        CurrentPoint_Lane5 = 1
        return [display_width * 0.6, display_height*0.4]
    elif(CurrentPoint_Lane5 == 1):
        CurrentPoint_Lane5 = 2
        return [display_width * 0.6, display_height*0.4+30]
    else:
        CurrentPoint_Lane5 = 0
        return [display_width * 0.6, display_height*0.4+60]


def getCurrentPointLane6():
    global CurrentPoint_Lane6
    if(CurrentPoint_Lane6 == 0):
        CurrentPoint_Lane6 = 1
        return [display_width*0.52, display_height*0.5]
    elif(CurrentPoint_Lane6 == 1):
        CurrentPoint_Lane6 = 2
        return [display_width*0.52+30, display_height*0.5]
    else:
        CurrentPoint_Lane6 = 0
        return [display_width*0.52+60, display_height*0.5]


def getCurrentPointLane4():
    global CurrentPoint_Lane4
    if(CurrentPoint_Lane4 == 0):
        CurrentPoint_Lane4 = 1
        return [display_width*0.52, 0]
    elif(CurrentPoint_Lane4 == 1):
        CurrentPoint_Lane4 = 2
        return [display_width*0.52+30, 0]
    else:
        CurrentPoint_Lane4 = 0
        return [display_width*0.52+60, 0]


def getDirectionLane1():
    global CurrentPoint_Lane1
    if CurrentPoint_Lane1 == 1:
        return "Straight"
    elif CurrentPoint_Lane1 == 2:
        return "Straight"
    else:
        return random.choice(["Straight", "Right", "Right"])


def getDirectionLane2():
    global CurrentPoint_Lane2
    if CurrentPoint_Lane2 == 1:
        return random.choice(["Straight", "Left", "Left"])
    elif CurrentPoint_Lane2 == 2:
        return "Straight"
    else:
        return random.choice(["Straight", "Right", "Right"])


def getDirectionLane4():
    global CurrentPoint_Lane4
    if CurrentPoint_Lane4 == 1:
        return "Straight"
    elif CurrentPoint_Lane4 == 2:
        return "Straight"
    else:
        return random.choice(["Straight", "Left", "Left"])


def removeCars():
    temp = []
    if(signalOn == 1):
        for i in ListLane1:
            if(i["CurrentPoint"][1] <= i["EndPoint"][1]):
                temp.append(i)
        for i in temp:
            ListLane1.remove(i)
            if(i["direction"] == "Straight"):
                i["CurrentPoint"] = getCurrentPointLane3()
                i["EndPoint"] = EndPoint_Lane3
                ListLane3.append(i)
            elif i["direction"] == "Right":
                i["CurrentPoint"] = getCurrentPointLane5()
                i["EndPoint"] = EndPoint_Lane5
                ListLane5.append(i)
    if(signalOn == 2):
        for i in ListLane2:
            if(i["CurrentPoint"][0] >= i["EndPoint"][0]):
                temp.append(i)
        for i in temp:
            ListLane2.remove(i)
            if(i["direction"] == "Straight"):
                i["CurrentPoint"] = getCurrentPointLane5()
                i["EndPoint"] = EndPoint_Lane5
                ListLane5.append(i)
            elif i["direction"] == "Left":
                i["CurrentPoint"] = getCurrentPointLane3()
                i["EndPoint"] = EndPoint_Lane3
                ListLane3.append(i)
            else:
                i["CurrentPoint"] = getCurrentPointLane6()
                i["EndPoint"] = EndPoint_Lane6
                ListLane6.append(i)

    if(signalOn == 3):
        for i in ListLane4:
            if(i["CurrentPoint"][1] >= i["EndPoint"][1]):
                temp.append(i)
        for i in temp:
            ListLane4.remove(i)
            if(i["direction"] == "Straight"):
                i["CurrentPoint"] = getCurrentPointLane6()
                i["EndPoint"] = EndPoint_Lane6
                ListLane6.append(i)
            else:
                i["CurrentPoint"] = getCurrentPointLane5()
                i["EndPoint"] = EndPoint_Lane5
                ListLane5.append(i)

        temp = []
        for i in ListLane1:
            if(i["CurrentPoint"][1] <= i["EndPoint"][1] and i["direction"] == "Straight"):
                temp.append(i)
        for i in temp:
            ListLane1.remove(i)
            i["CurrentPoint"] = getCurrentPointLane3()
            i["EndPoint"] = EndPoint_Lane3
            ListLane3.append(i)
    # print(ListLane3)


start_ticks = pygame.time.get_ticks()
counter = 0
TimeSignal1 = laneTime[counter][0]
TimeSignal2 = laneTime[counter][1]
TimeSignal3 = laneTime[counter][2]
counter += 1

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == EVENT_SECOND:
            if signalOn == 1:
                TimeSignal1 -= 1
                if TimeSignal1 == 0:
                    print("Signal 2")
                    signalOn = 2
                    #TimeSignal1 = laneTime[counter][1]
                    signalLane1 = signalRed
                    signalLane3 = signal3Red
                    signalLane2 = signal2
            elif signalOn == 2:
                TimeSignal2 -= 1
                if TimeSignal2 == 0:
                    print("Signal 3")
                    signalOn = 3
                    #TimeSignal2 = laneTime[counter][2]
                    signalLane1 = signal1Straight
                    signalLane2 = signal2Red
                    signalLane3 = signal3
            elif signalOn == 3:
                TimeSignal3 -= 1
                if TimeSignal3 == 0:
                    #Signal 3 gets over so i increment counter and do setup
                    TimeSignal1 = laneTime[counter][0]
                    TimeSignal2 = laneTime[counter][1]
                    TimeSignal3 = laneTime[counter][2]
                    counter += 1
                    #######################################################
                    print("Signal 1")
                    signalOn = 1
                    signalLane1 = signal1
                    signalLane2 = signal2Red
                    signalLane3 = signal3Red
            else:
                print("Signal 1")
                signalOn = 1
                signalLane1 = signal1
                signalLane2 = signal2Red
                signalLane3 = signal3Red
        # if(counter%10 == 0):
        #     if signalOn == 1:
        #         print("Signal 2")
        #         signalOn = 2
        #         signalLane1 = signalRed
        #         signalLane3 = signal3Red
        #         signalLane2 = signal2
        #     elif signalOn == 2:
        #         print("Signal 3")
        #         signalOn = 3
        #         signalLane1 = signal1Straight
        #         signalLane2 = signal2Red
        #         signalLane3 = signal3
        #     elif signalOn == 3:
        #         print("Signal 1")
        #         signalOn = 1
        #         signalLane1 = signal1
        #         signalLane2 = signal2Red
        #         signalLane3 = signal3Red
        #     else:
        #         print("Signal 1")
        #         signalOn = 1
        #         signalLane1 = signal1
        #         signalLane2 = signal2Red
        #         signalLane3 = signal3Red

    current_second = datetime.datetime.now().strftime("%S")
    if(not current_second == second):
        second = current_second
        found = False
        for i in DataLane1:
            current_time = parser.parse(i['time']).strftime("%H:%M:%S")
            if(current_time == time.strftime("%H:%M:%S") and i['direction'] == "in"):
                currentPoint = getCurrentPointLane1()
                ListLane1.append({"id": id, "type": i["type"], "direction": getDirectionLane1(
                ), "EndPoint": EndPoint_Lane1, "CurrentPoint": currentPoint})
                id += 1

                currentPoint = getCurrentPointLane2()
                ListLane2.append({"id": id, "type": i["type"], "direction": getDirectionLane2(
                ), "EndPoint": EndPoint_Lane2, "CurrentPoint": currentPoint})
                id += 1

                currentPoint = getCurrentPointLane4()
                ListLane4.append({"id": id, "type": i["type"], "direction": getDirectionLane4(
                ), "EndPoint": EndPoint_Lane4, "CurrentPoint": currentPoint})
                id += 1

                found = True
            else:
                if(found == True):
                    break
        # for i in DataLane2:
        #     current_time = parser.parse(i['time']).strftime("%H:%M:%S")
        #     if(current_time == time.strftime("%H:%M:%S") and i['direction'] == "in"):
        #         currentPoint = getCurrentPointLane2()
        #         ListLane2.append({"id": id, "type": i["type"], "direction": getDirectionLane2(
        #         ), "EndPoint": EndPoint_Lane2, "CurrentPoint": currentPoint})
        #         id += 1
        # for i in DataLane3:
        #     current_time = parser.parse(i['time']).strftime("%H:%M:%S")
        #     if(current_time == time.strftime("%H:%M:%S") and i['direction'] == "in"):
        #         currentPoint = getCurrentPointLane4()
        #         ListLane4.append({"id": id, "type": i["type"], "direction": getDirectionLane4(
        #         ), "EndPoint": EndPoint_Lane4, "CurrentPoint": currentPoint})
        #         id += 1
        if time.strftime("%H:%M:%S") == final_time.strftime("%H:%M:%S"):
            crashed = True
        # Increment time by 1 second
        time = time + datetime.timedelta(seconds=1)

        #############################################
    movePosition()
    removeCars()
    render()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
