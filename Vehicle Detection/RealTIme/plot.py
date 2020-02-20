import matplotlib.pyplot as plt 
import json
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

with open('output.txt') as f:
    data = json.load(f)["list"]
#print(data)

yVehicles = []
yCars = []
yTrucks = []
yPercentage = []
ySpeed = []
x = []
for item in data:
    x.append(int(item["frameNo"]))
    yVehicles.append(int(item["Vehicles"]))
    yCars.append(int(item["Cars"]))
    yTrucks.append(int(item["Trucks"]))
    yPercentage.append(float(item["Percentage"]))
    ySpeed.append(float(item["Speed"]))

xSmooth = np.linspace(min(x), max(x), 100)
spl = make_interp_spline(x, yPercentage, k=11)
yPercentageSmooth = spl(xSmooth)

spl = make_interp_spline(x, ySpeed, k=11)
ySpeedSmooth = spl(xSmooth)

# Speed & Percentage 
plt.figure(1)
plt.plot(x, ySpeed, label = "Speed")
#plt.plot(xSmooth, ySpeedSmooth, label = "Speed Smooth")
plt.plot(x, yPercentage, label = "Percentage")
#plt.plot(xSmooth, yPercentageSmooth, label = "Percentage Smooth")
plt.xlabel('x - axis')
plt.ylabel('Frame no.')
plt.title('Speed & Percentage')
plt.legend()

# Vehicles, Cars & Trucks
plt.figure(2)
activities = ['Cars', 'Trucks'] 
slices = [yCars[-1], yTrucks[-1]] 
colors = ['r', 'y']
plt.pie(slices, labels = activities, colors=colors,  
        startangle=90, shadow = True, explode = (0, 0), 
        radius = 1.2, autopct = make_autopct(slices)) 
plt.title('Total Number of Vehicles: ' + str(yVehicles[-1]))
plt.legend() 
plt.show()
