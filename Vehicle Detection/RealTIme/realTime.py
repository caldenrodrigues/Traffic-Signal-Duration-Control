import os
import logging
import logging.handlers
import random
import math
import numpy as np
import skvideo.io
import cv2 as cv2
import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import utils
import datetime
import json

# import utils
# without this some strange errors happen
cv2.ocl.setUseOpenCL(False)
random.seed(123)


# ============================================================================
IMAGE_SOURCE = "./lowDensity.png"
VIDEO_SOURCE = "./full_length.m4v"
# VIDEO_SOURCE = "shutterstock.mp4"
SHOW_OUTPUT = False
SHAPE = (720, 1280)  # HxW
EXIT_COLOR = (66, 183, 42)

# EXIT_PTS = np.array([
#     [[627, 160], [600, 160], [784, 720], [1280, 720], [1280, 465]]
# ])
EXIT_PTS = np.array([
    [[710, 0], [600, 0], [780, 455], [1177, 400]]
])
base = np.zeros(SHAPE + (3,), dtype='uint8')
exit_mask = cv2.fillPoly(base, EXIT_PTS, (255, 255, 255))[
    :, :, 0]  # RGB for background mask

options = {"model": "../Yolo/cfg/yolo.cfg",
           "load": "../Yolo/bin/yolo.weights", "threshold": 0.1, "gpu": 0.8}

tfnet = TFNet(options)
pathes = []
data = {}
data['list'] = []
simulation = {}
simulation['list'] = []
speedForOnePixelPerFrame = 4
vehicle_count = 0
car_count = 0
truck_count = 0
bike_count = 0
min_contour_width = 35
min_contour_height = 35
max_contour_width = 330
max_contour_height = 330
x_weight = 1.0
y_weight = 2.0
max_dst = 30
path_size = 4
BOUNDING_BOX_COLOUR = (255, 0, 0)
CAR_COLOURS = [(0, 0, 255)]
# ============================================================================


def distance(y):
    y = 720-y
    return max(1, (y-207.5)/10.25)


def max(x, y):
    if(x > y):
        return x
    return y


sum_of_exit_mask = 0
row = 0
for outer in exit_mask:
    sum_of_exit_mask += np.count_nonzero(outer == 255) * distance(row)
    row += 1


def show_me(img, show_output=False, text="Image"):
    if show_output:
        print("--- " + text + " ---")
        plt.imshow(img)
        plt.show()


def train_bg_subtractor(inst, cap, num=500):
    print('Training BG Subtractor...')
    i = 0
    for frame in cap:
        inst.apply(frame, None, 0.001)
        plt.show()
        i += 1
        if i >= num:
            return cap


def filter_mask(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # Fill any small holes
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # Remove noise
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    # Dilate to merge adjacent blobs
    dilation = cv2.dilate(opening, kernel, iterations=5)

    return dilation


def main():
    # creating exit mask from points, where we will be counting our vehicles
    global exit_mask
    global vehicle_count
    global car_count
    global truck_count
    global bike_count
    global sum_of_exit_mask

    img = cv2.imread(IMAGE_SOURCE)

    _img = np.zeros(img.shape, img.dtype)
    _img[:, :] = EXIT_COLOR
    mask = cv2.bitwise_and(_img, _img, mask=exit_mask)
    cv2.addWeighted(mask, 1, img, 1, 0, img)
    show_me(img, text="Added weigth to mask", show_output=SHOW_OUTPUT)

    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500, detectShadows=True)

    capRun = skvideo.io.vreader(VIDEO_SOURCE)

    vidObj = cv2.VideoCapture(VIDEO_SOURCE)
    old_time = datetime.datetime.now()

    # skipping 500 frames to train bg subtractor
    train_bg_subtractor(bg_subtractor, capRun, num=500)

    _frame_number = -1
    frame_number = -1
    pathes = []
    for frame in capRun:
        if not frame.any():
            print("Frame capture failed, stopping...")
            break

        do_not_need1, do_not_need2 = vidObj.read()

        _frame_number += 1
        if _frame_number % 2 != 0:
            continue
        frame_number += 1

        show_me(frame, text="Frame " + str(frame_number),
                show_output=SHOW_OUTPUT)
        fg_mask = bg_subtractor.apply(frame, None, 0.001)
        show_me(fg_mask, text="After Background Subtraction",
                show_output=SHOW_OUTPUT)
        # fg_mask[fg_mask < 175] = 0
        # show_me(fg_mask, text="Frame after thresholding",
        #         show_output=SHOW_OUTPUT)

        # # Perform morphology
        # se = np.ones((7, 7), dtype='uint8')
        # image_close = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, se)

        # show_me(image_close, text="Mask",
        #         show_output=SHOW_OUTPUT)

        fg_mask[fg_mask < 175] = 0
        show_me(fg_mask, text="Frame after thresholding",
                show_output=SHOW_OUTPUT)
        fg_mask = filter_mask(fg_mask)
        show_me(fg_mask, text="Frame after filtering", show_output=SHOW_OUTPUT)

        fg_mask_area = cv2.bitwise_and(fg_mask, fg_mask, mask=exit_mask)
        show_me(fg_mask_area, text="Frame after BitWise And",
                show_output=SHOW_OUTPUT)

        sum_of_fg_mask = 0
        row = 0
        for outer in fg_mask_area:
            # print(outer)
            # print(type(outer))
            #sum_of_fg_mask += list(outer).count(255) * distance(row)
            sum_of_fg_mask += np.count_nonzero(outer == 255) * distance(row)
            row += 1

        percentageActual = (sum_of_fg_mask / sum_of_exit_mask) * 100
        #print("Percentage calculated with distance considered: " + str(percentageActual))

        # percentage = cv2.countNonZero(
        #     fg_mask_area) / (cv2.countNonZero(exit_mask)) * 100
        # print("Percentage calculated without distance considered: " + str(percentage))

        # print(len(_img.shape))
        temp = cv2.merge((fg_mask_area, fg_mask_area, fg_mask_area))
        mask = cv2.bitwise_and(_img, _img, mask=exit_mask)
        cv2.addWeighted(mask, 1, temp, 1, 0, temp)
        show_me(frame, text="Frame after Percentage", show_output=SHOW_OUTPUT)

        # objects Detected
        matches = []

        # Pass the image into the NN
        result = tfnet.return_predict(frame)
        #print("Count1:" + str(len(result)))

        for detected in result:
            l = detected["label"]
            x = detected["topleft"]["x"]
            y = detected["topleft"]["y"]
            w = detected["bottomright"]["x"] - detected["topleft"]["x"]
            h = detected["bottomright"]["y"] - detected["topleft"]["y"]
            # print(l,x,y,w,h)
            contour_valid = (w >= min_contour_width) and (h >= min_contour_height) and (
                w <= max_contour_width) and (h <= max_contour_height)
            if not contour_valid:
                continue
            centroid = utils.get_centroid(x, y, w, h)
            matches.append((l, (x, y, w, h), centroid))
        if not pathes:
            # print("Creating Pathes")
            for match in matches:
                pathes.append([match])
        else:
            new_pathes = []
            for path in pathes:
                # print("Initial path is: ",path)
                _min = 999999
                _match = None
                for p in matches:
                    if(len(path) == 1):
                        d = utils.distance(p[1], path[-1][1])
                    else:
                        # eg: [2,4,6] -> 2*4 - 2 = 6
                        xn = 2 * path[-1][1][0] - path[-2][1][0]
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
                    # print("Found point: ",_match)
                    matches.remove(_match)  # Remove form current points
                    path.append(_match)  # Add to path
                    # print("Path is: ",path)
                    # Have a list of new paths incase a point did not move
                    new_pathes.append(path)
                # do not drop path if current frame has no matches
                if _match is None:
                    new_pathes.append(path)
            pathes = new_pathes
            if len(matches):
                for p in matches:
                    # print(p)
                    # do not add points that already should be counted
                    # if check_exit(p[2]):
                    #     continue
                    pathes.append([p])
        # save only last N points in every path in pathes
        for i, _ in enumerate(pathes):
            pathes[i] = pathes[i][path_size * -1:]
        # print(pathes)
        # Count vehicles entering exit zone
        new_pathes = []
        for i, path in enumerate(pathes):
            d = path[-2:]
            if (
                # need at least two points to count
                len(d) >= 2 and
                # prev point not in exit zone
                check_exit(d[0][2]) and
                # current point in exit zone
                not check_exit(d[1][2]) and
                # path len is bigger then min
                path_size <= len(path)
            ):
                vehicle_count += 1
                vehicle = 'car'
                if(path[-1][0] == 'car'):
                    car_count += 1
                if(path[-1][0] == 'truck'):
                    vehicle = 'truck'
                    truck_count += 1
                # if(path[-1][0] == 'motorbike'):
                #     bike_count += 1
                # Adding timestamp to data
                msec = vidObj.get(cv2.CAP_PROP_POS_MSEC)
                time = old_time + datetime.timedelta(milliseconds=msec)
                # Adding direction to data
                simulation['list'].append(
                   {'time': time, 'type': vehicle, 'direction': 'in'})
                # print(data)
                new_pathes.append(path)
            else:
                # prevent linking with path that already in exit zone
                # add = True
                # for p in path:
                #     if check_exit(p[2]):
                #         add = False
                #         break
                # if add:
                #     new_pathes.append(path)
                new_pathes.append(path)
        pathes = new_pathes
        #################################################
        # Speed
        #################################################
        # print(pathes)
        sumPixelDifference = 0
        for path in pathes:
            if len(path) > 1:
                sumPixelDifference += utils.distance(path[-1][2], path[-2][2])
                # print(sumPixelDifference)
        # print("-------------------")
        #print(sumPixelDifference / len(pathes))
        avgSpeed = sumPixelDifference / len(pathes) * speedForOnePixelPerFrame
        #print("Count2: " + str(len(pathes)))
        #################################################
        # VISUALIZATION
        #################################################
        # TOP BAR
        cv2.rectangle(
            frame, (0, 0), (frame.shape[1], 50), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, ("Vehicles: {total} - Cars: {cars} - Trucks: {trucks} - Percentage: {percentage} - Avg Speed: {avgSpeed}km/hr".format(
            total=vehicle_count, cars=car_count, trucks=truck_count, percentage=str("{0:.2f}".format(percentageActual)), avgSpeed=str("{0:.2f}".format(avgSpeed)))), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        # MASK1
        # print(exit_mask)
        _frame = np.zeros(frame.shape, frame.dtype)
        # show_me(_img, text = "Numpy array initialized to zeros",show_output = self.show_output)
        _frame[:, :] = EXIT_COLOR
        # show_me(_img, text = "Set it to green",show_output = self.show_output)
        mask = cv2.bitwise_and(_frame, _frame, mask=exit_mask)
        # show_me(mask, text = "Set Mask color",show_output = SHOW_OUTPUT)
        cv2.addWeighted(mask, 1, frame, 1, 0, frame)
        show_me(frame, text="Added weigth to mask",
                show_output=SHOW_OUTPUT)
        # BOXES
        # PATHS
        # print(pathes)
        for i, path in enumerate(pathes):
            # print(path)
            centroid = np.array(path)[:, 2].tolist()
            contour = path[-1][1]
            # print(contour)
            x, y, w, h = contour
            cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1),
                          BOUNDING_BOX_COLOUR, 1)
            for point in centroid:
                cv2.circle(frame, point, 2, CAR_COLOURS[0], -1)
                cv2.polylines(frame, [np.int32(centroid)],
                              False, CAR_COLOURS[0], 1)
        show_me(frame, text="Created Paths", show_output=SHOW_OUTPUT)
        print("Vehicle Count: " + str(vehicle_count))
        utils.save_frame(frame, "OUTPUT/processed_%04d.png" % frame_number)
        data["list"].append({"frameNo":frame_number, "Vehicles": vehicle_count, "Cars": car_count, "Trucks": truck_count, "Percentage": str(
            "{0:.2f}".format(percentageActual)), "Speed": str("{0:.2f}".format(avgSpeed))})
        with open('output.txt','w') as jsonFile:
            json.dump(data, jsonFile, default = myconverter)
        with open('simulation.txt','w') as jsonFile:
            json.dump(simulation, jsonFile, default = myconverter)


# ============================================================================

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def check_exit(point):
    # show_me(exit_masks1[0],True,"WTF1")
    # show_me(exit_masks2[0],True,"WTF2")
    global exit_mask
    # for mask in exit_mask:
    #     print(mask)
    #     #show_me(exit_mask,True,"Exitmask")
    #     try:
    #         if mask[point[1]][point[0]] == 255:
    #             return 1
    #     except:
    #         return 1
    try:
        if exit_mask[point[1]][point[0]] == 255:
            return 1
    except:
        return 1
    return False


if __name__ == "__main__":
    # log = utils.init_logging()

    main()
