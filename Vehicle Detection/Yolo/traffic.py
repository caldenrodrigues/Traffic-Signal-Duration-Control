import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
import skvideo.io
from darkflow.net.build import TFNet
import utils
import json
import datetime

def show_me(img, show_output=False, text="Image"):
    if show_output:
        print(text)
        plt.imshow(img)
        plt.show()

IMAGE_DIR = "./Output"
VIDEO_SOURCE = "../Videos/demo_lane.mp4"
SHOW_OUTPUT = False
SHAPE = (720, 1280)  # HxW
EXIT_PTS1 = np.array([
    [[0, 400], [645, 500], [645, 0], [0, 0]]
])
EXIT_PTS2 = np.array([
    [[732, 720], [732, 590], [1280, 500], [1280, 720]]
])
'''

'''
options = {"model": "cfg/yolo.cfg", "load": "bin/yolo.weights", "threshold": 0.1, "gpu": 0.8}
min_contour_width = 35
min_contour_height = 35
max_contour_width = 330
max_contour_height = 330
BOUNDING_BOX_COLOUR = (255, 0, 0)
CAR_COLOURS = [(0, 0, 255)]
EXIT_COLOR = (66, 183, 42)
x_weight = 1.0
y_weight = 2.0
max_dst = 30
base = np.zeros(SHAPE + (3,), dtype='uint8')
base_cp = np.zeros(SHAPE + (3,), dtype='uint8')
#Filling the exit_mask
exit_masks1 = [cv2.fillPoly(base, EXIT_PTS1, (255, 255, 255))[:, :, 0]]	#RGB for background mask
exit_masks2 = [cv2.fillPoly(base_cp, EXIT_PTS2, (255, 255, 255))[:, :, 0]]
path_size = 4


def main():
    tfnet = TFNet(options)
    pathes = []
    vehicle_count = 0
    car_count = 0
    truck_count = 0
    #show_me(exit_masks, SHOW_OUTPUT, "Exit Mask")
    #Capture the video
    #cap = skvideo.io.vreader(VIDEO_SOURCE)
    vidObj = cv2.VideoCapture(VIDEO_SOURCE)
    success = 1
    #Code to skip every second frame
    _frame_number = -1
    frame_number = -1
    #for frame in cap:
    data = {}
    data['list'] = []
    old_time = datetime.datetime.now()
    msec = 0
    while success:
        '''
        if not frame.any():
            print("Frame capture failed, stopping...")
            break
        '''
        success, frame = vidObj.read()

        # real frame number
        _frame_number += 1
        # skip every 2nd frame to speed up processing
        if _frame_number % 2 != 0:
            continue
        frame_number += 1
        show_me(frame,SHOW_OUTPUT,frame_number)

        #objects Detected
        matches = []

        #Pass the image into the NN
        result = tfnet.return_predict(frame)
        #print(result)
        #Representing in terms of top left point and removing max, min objects
        for detected in result:
            l = detected["label"]
            x = detected["topleft"]["x"]
            y = detected["topleft"]["y"]
            w = detected["bottomright"]["x"] - detected["topleft"]["x"]
            h = detected["bottomright"]["y"] - detected["topleft"]["y"]
            #print(l,x,y,w,h)
            contour_valid = (w >= min_contour_width) and (h >= min_contour_height) and (w <= max_contour_width) and (h <= max_contour_height)
            if not contour_valid:
                continue
            centroid = utils.get_centroid(x, y, w, h)
            matches.append((l,(x,y,w,h),centroid))
            #cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1),BOUNDING_BOX_COLOUR, 1)
        #show_me(frame, SHOW_OUTPUT, "Vehicle Detected")
        #print("Matches is: ",matches)
        #Vehicle Counting
        if not pathes:
            #print("Creating Pathes")
            for match in matches:
                pathes.append([match])
        else:
            new_pathes = []
            for path in pathes:
                #print("Initial path is: ",path)
                _min = 999999
                _match = None
                for p in matches:
                    if(len(path) == 1):
                        d = utils.distance(p[1], path[-1][1])
                    else:
                        xn = 2 * path[-1][1][0] - path[-2][1][0] # eg: [2,4,6] -> 2*4 - 2 = 6
                        yn = 2 * path[-1][1][1] - path[-2][1][1]
                        d = utils.distance(
                            p[1], (xn, yn),
                            x_weight=x_weight,
                            y_weight=y_weight
                        )
                    if d < _min:
                        _min = d
                        _match = p
                if _match and _min <= max_dst:
                    #print("Found point: ",_match)
                    matches.remove(_match)   #Remove form current points
                    path.append(_match)     #Add to path
                    #print("Path is: ",path)
                    new_pathes.append(path) #Have a list of new paths incase a point did not move
                # do not drop path if current frame has no matches
                if _match is None:
                    new_pathes.append(path)
            pathes = new_pathes
            if len(matches):
                for p in matches:
                    #print(p)
                    # do not add points that already should be counted
                    if check_exit(p[2]):
                        continue
                    pathes.append([p])
        # save only last N points in every path in pathes
        for i, _ in enumerate(pathes):
            pathes[i] = pathes[i][path_size * -1:]
        #print(pathes)
        #Count vehicles entering exit zone
        new_pathes = []
        for i, path in enumerate(pathes):
            d = path[-2:]
            if (
                # need at least two points to count
                len(d) >= 2 and
                # prev point not in exit zone
                not check_exit(d[0][2]) and
                # current point in exit zone
                check_exit(d[1][2]) and
                # path len is bigger then min
                path_size <= len(path)
            ):
                vehicle_count += 1
                if(path[-1][0] == 'car'):
                    car_count +=1
                if(path[-1][0] == 'truck'):
                    truck_count +=1
                #Adding timestamp to data
                msec = vidObj.get(cv2.CAP_PROP_POS_MSEC)
                time = old_time + datetime.timedelta(milliseconds=msec)
                #Adding direction to data
                if(check_exit(d[1][2]) == 1):
                    direction = "in"
                else:
                    direction = "out"
                data['list'].append({'time':time,'type':'car','direction':direction})
                #print(data)
            else:
                # prevent linking with path that already in exit zone
                add = True
                for p in path:
                    if check_exit(p[2]):
                        add = False
                        break
                if add:
                    new_pathes.append(path)

        pathes = new_pathes
        #################################################
        #VISUALIZATION
        #################################################
        #TOP BAR
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, ("Vehicles passed: {total} --- Cars passed: {cars} --- Trucks passed: {trucks}".format(total=vehicle_count,cars=car_count,trucks=truck_count)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        #MASK1
        for exit_mask in exit_masks1:
            #print(exit_mask)
            _frame = np.zeros(frame.shape, frame.dtype)
            #show_me(_img, text = "Numpy array initialized to zeros",show_output = self.show_output)
            _frame[:, :] = EXIT_COLOR
            #show_me(_img, text = "Set it to green",show_output = self.show_output)
            mask = cv2.bitwise_and(_frame, _frame, mask=exit_mask)
            #show_me(mask, text = "Set Mask color",show_output = SHOW_OUTPUT)
            cv2.addWeighted(mask, 1, frame, 1, 0, frame)
            show_me(frame, text = "Added weigth to mask",show_output = SHOW_OUTPUT)
        #MASK2
        for exit_mask in exit_masks2:
            #print(exit_mask)
            _frame = np.zeros(frame.shape, frame.dtype)
            #show_me(_img, text = "Numpy array initialized to zeros",show_output = self.show_output)
            _frame[:, :] = EXIT_COLOR
            #show_me(_img, text = "Set it to green",show_output = self.show_output)
            mask = cv2.bitwise_and(_frame, _frame, mask=exit_mask)
            #show_me(mask, text = "Set Mask color",show_output = SHOW_OUTPUT)
            cv2.addWeighted(mask, 1, frame, 1, 0, frame)
            show_me(frame, text = "Added weigth to mask",show_output = SHOW_OUTPUT)
        #BOXES
        #PATHS
        for i, path in enumerate(pathes):
            #print(path)
            centroid = np.array(path)[:, 2].tolist()
            contour = path[-1][1]
            #print(contour)
            x,y,w,h = contour
            cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), BOUNDING_BOX_COLOUR, 1)
            for point in centroid:
                cv2.circle(frame, point, 2, CAR_COLOURS[0], -1)
                cv2.polylines(frame, [np.int32(centroid)], False, CAR_COLOURS[0], 1)
        show_me(frame, text = "Created Paths",show_output = SHOW_OUTPUT)
        #SAVE FRAME
        utils.save_frame(frame, IMAGE_DIR +
                         "/processed_%04d.png" % frame_number)
    with open('output.txt','w') as jsonFile:
        json.dump(data, jsonFile, default = myconverter)

def check_exit(point):
    #show_me(exit_masks1[0],True,"WTF1")
    #show_me(exit_masks2[0],True,"WTF2")
    for exit_mask in exit_masks1:
        #show_me(exit_mask,True,"Exitmask")
        try:
            if exit_mask[point[1]][point[0]] == 255:
                return 1
        except:
            return 1
    for exit_mask in exit_masks2:
        #show_me(exit_mask,True,"Exitmask")
        try:
            if exit_mask[point[1]][point[0]] == 255:
                return 2
        except:
            return 2
    return False

def show_me(img, show_output=False, text="Image"):
    if show_output:
        print(text)
        plt.imshow(img)
        plt.show()

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

if __name__ == "__main__":
    if not os.path.exists(IMAGE_DIR):
        log.debug("Creating image directory `%s`...", IMAGE_DIR)
        os.makedirs(IMAGE_DIR)
    main()
