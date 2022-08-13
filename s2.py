import pygame as pg
import numpy as np
import math

pg.init()
display = pg.display.set_mode((1000, 700), 0, 32)
g = 10
r_const = 10
coordinates = []
coordinates_square = []

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to Inter Universe Space server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

universe_id = 0

def initialize_universe(number_of_balls, center_x, center_y, angle):
    global coordinates
    global coordinates_square
    coordinates = []
    coordinates_square = []
    x_center, y_center = display.get_width() / center_x, display.get_height() / center_y

    for i in range(1,number_of_balls):
        x, y = pol2cart(((i*200)/200)*20, math.radians((i*200)))
        circle = draw_circle(x_center-x,y_center-y,10)
        coordinates.append([x_center+x,y_center+y])

def get_centroide(indexes):
    centroide = [0, 0]
    for i in range(0,len(coordinates)):
        if i in indexes or str(i) in indexes:
            centroide[0] += coordinates[i][0]
            centroide[1] += coordinates[i][1]
    centroide[0] = centroide[0] / len(indexes)
    centroide[1] = centroide[1] / len(indexes)
    return centroide

def find_direction_of_vector(x1,y1,x2,y2):
    return math.atan((y1-y2)/(x1-x2));

def getDistance(x1,x2,y1,y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 1/2

def find_intesity_of_vector(x1,y1,m1,x2,y2,m2):
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 1/2
    return g * (m1 * m2)/ distance

def decompose_vector(angle, f_intesity):
    fx = f_intesity * math.cos(angle)
    fy = f_intesity * math.sin(angle)
    return (fx,fy)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def draw_circle(x,y,r):
    return pg.draw.circle(display, [255, 255, 255, 255], (x, y), r)

def create_square():
    distancies = {}
    clusters = {}
    cluster_dict = {}
    global coordinates
    for i in range(0,len(coordinates)):
        coord = coordinates[i]
        for j in range(0,len(coordinates)):
            if(i == j):
                continue
            coord2 = coordinates[j]
            distancies[str(i)+'-'+str(j)] = (abs(coord[0] - coord2[0]), abs(coord[1] - coord2[1]))

    cluster_index = 1

    keys = []
    for dist in distancies:
        keys.append(dist)

    for dist in keys:
        if(distancies[dist][0] <= 3 and distancies[dist][1] <= 3):
            integrants = dist.split('-')
            if integrants[0] not in cluster_dict and integrants[1] not in cluster_dict:
                clusters[cluster_index] = []
                clusters[cluster_index].append(integrants[0])
                clusters[cluster_index].append(integrants[1])
                cluster_dict[integrants[0]] = cluster_index
                cluster_dict[integrants[1]] = cluster_index
                cluster_index += 1
            elif integrants[0] in cluster_dict:
                if integrants[1] not in cluster_dict:
                    clusters[cluster_dict[integrants[0]]].append(integrants[1])
                    cluster_dict[integrants[1]] = cluster_dict[integrants[0]]
            else:
                if integrants[0] not in cluster_dict:
                    clusters[cluster_dict[integrants[1]]].append(integrants[0])
                    cluster_dict[integrants[0]] = cluster_dict[integrants[1]]

    for cluster in clusters:
        if(len(clusters[cluster]) == 7):
            print(cluster,' ',clusters[cluster])
            centroide = get_centroide(clusters[cluster])
            print('clusters[cluster] ',clusters[cluster])
            coordinates_square.append([centroide[0],centroide[1]])
            print('centroide ',[centroide[0],centroide[1]])
            coordinates3 = []
            for i in range(0,len(coordinates)):
                if(str(i) not in clusters[cluster]):
                    coordinates3.append(coordinates[i])
            print('before ', coordinates)
            coordinates = coordinates3
            print('after ', coordinates)
            pg.draw.rect(display,[26, 173, 255,255],pg.Rect(centroide[0], centroide[1], 30, 30), 0)
    return

def create_circle():
    centroide = [0, 0]
    for i in range(0, len(coordinates)):
        centroide[0] += coordinates[i][0]
        centroide[1] += coordinates[i][1]

    for i in range(0, len(coordinates_square)):
        centroide[0] += coordinates_square[i][0]
        centroide[1] += coordinates_square[i][1]

    centroide[0] = centroide[0] / (len(coordinates)+len(coordinates_square))
    centroide[1] = centroide[1] / (len(coordinates)+len(coordinates_square))

    socket.send((str(universe_id)+"#"+str(centroide[0])+"#"+str(centroide[1])).encode())
    message = socket.recv()

    centroide_received = message.decode("utf-8")
    x = float(centroide_received.split("#")[0])
    y = float(centroide_received.split("#")[1])

    draw_circle(x,y,r_const)
    coordinates.append([x,y])

def calculate_resulting_point(x,y):
    x1 = x
    y1 =  y

    fx_sum = 0
    fy_sum = 0
    total = 0

    position = 0

    for coord in coordinates:
        x2 = coord[0]
        y2 = coord[1]
        if x1 == x2 and y1 == y2:
            position = total
        total+=1

    vectors = []
    for coord in coordinates:
        x2 = coord[0]
        y2 = coord[1]

        # print(x1, x2, y1, y2)
        if x1 == x2 and y1 == y2:
            continue

        if abs(x1 - x2) < 4 and abs(y1 - y2) < 4:
            continue

        fx, fy = decompose_vector(find_direction_of_vector(x1, y1, x2, y2),
                                  find_intesity_of_vector(x1, y1, 8, x2, y2, 8))

        initial_distance = getDistance(x1,y1,x2,y2)
        if((x1<x2 and x1<x1+fx<x2) or (x1<x2 and x1<x2<x1+fx)):
            pg.draw.line(display, [5, 255, 255], (x1,y1), (x1+fx*1300,y1+fy*1300),2)
            vectors.append([[x1,y1],[x1+fx,y1+fy]])
        else:
            pg.draw.line(display, [5, 255, 255], (x1, y1), (x1 - fx*1300, y1 - fy*1300), 2)
            vectors.append([[x1, y1], [x1 - fx, y1 - fy]])

        total += 1

    ############

    for coord in coordinates_square:
        x2 = coord[0]
        y2 = coord[1]

        fx, fy = decompose_vector(find_direction_of_vector(x1, y1, x2, y2),
                                  find_intesity_of_vector(x1, y1, 8, x2, y2, 8*8))

        if((x1<x2 and x1<x1+fx<x2) or (x1<x2 and x1<x2<x1+fx)):
            pg.draw.line(display, [5, 255, 255], (x1,y1), (x1-fx*1300,y1-fy*1300),2)
            vectors.append([[x1,y1],[x1-fx,y1-fy]])
        else:
            pg.draw.line(display, [5, 255, 255], (x1, y1), (x1 + fx*1300, y1 + fy*1300), 2)
            vectors.append([[x1, y1], [x1 + fx, y1 + fy]])

        total += 1

    resulting_vector = [[0,0],[0,0]]
    for vector in vectors:
        resulting_vector[0][0] += vector[0][0]
        resulting_vector[0][1] += vector[0][1]
        resulting_vector[1][0] += vector[1][0]
        resulting_vector[1][1] += vector[1][1]

    if(len(vectors)>0):
        resulting_vector[0][0] = resulting_vector[0][0]/len(vectors)
        resulting_vector[0][1] = resulting_vector[0][1] / len(vectors)
        resulting_vector[1][0] = resulting_vector[1][0] / len(vectors)
        resulting_vector[1][1] = resulting_vector[1][1] / len(vectors)

    # print('resulting ', resulting_vector[0], resulting_vector[1])
    pg.draw.line(display, [5, 5, 255], resulting_vector[0], resulting_vector[1], 2)
    return (resulting_vector[0],resulting_vector[1], position)

def calculate_square_resulting_point(x,y):
    x1 = x
    y1 =y
    total = 0

    position = 0

    for coord in coordinates_square:
        x2 = coord[0]
        y2 = coord[1]
        if x1 == x2 and y1 == y2:
            position = total
        total+=1

    vectors = []
    for coord in coordinates:
        x2 = coord[0]
        y2 = coord[1]

        if abs(x1 - x2) < 5 and abs(y1 - y2) < 5:
            continue

        fx, fy = decompose_vector(find_direction_of_vector(x1, y1, x2, y2),
                                  find_intesity_of_vector(x1, y1, 8*8, x2, y2, 8))

        initial_distance = getDistance(x1,y1,x2,y2)
        if((x1<x2 and x1<x1+fx<x2) or (x1<x2 and x1<x2<x1+fx)):
            pg.draw.line(display, [5, 255, 255], (x1,y1), (x1- fx*1300/8,y1-fy*1300/8),2)
            vectors.append([[x1,y1],[x1-fx/8,y1-fy/8]])
        else:
            pg.draw.line(display, [5, 255, 255], (x1, y1), (x1 + fx*1300/8, y1 + fy*1300/8), 2)
            vectors.append([[x1, y1], [x1 + fx/8, y1 + fy/8]])

        total += 1

    for coord2 in coordinates_square:
        x2 = coord2[0]
        y2 = coord2[1]

        if abs(x1 - x2) < 5 and abs(y1 - y2) < 5:
            continue

        fx, fy = decompose_vector(find_direction_of_vector(x1, y1, x2, y2),
                                  find_intesity_of_vector(x1, y1, 20, x2, y2, 20))

        initial_distance = getDistance(x1,y1,x2,y2)
        if((x1<x2 and x1<x1+fx<x2) or (x1<x2 and x1<x2<x1+fx)):
            pg.draw.line(display, [5, 255, 255], (x1,y1), (x1+ fx*1300,y1+fy*1300),2)
            vectors.append([[x1,y1],[x1+fx,y1+fy]])
        else:
            pg.draw.line(display, [5, 255, 255], (x1, y1), (x1 - fx*1300, y1 - fy*1300), 2)
            vectors.append([[x1, y1], [x1 - fx, y1 - fy]])

        total += 1

    ############

    # for coord in coordinates_square:
    #     x2 = coord[0]
    #     y2 = coord[1]
    #
    #     fx, fy = decompose_vector(find_direction_of_vector(x1, y1, x2, y2),
    #                               find_intesity_of_vector(x1, y1, 2, x2, y2, 2))
    #
    #     if((x1<x2 and x1<x1+fx<x2) or (x1<x2 and x1<x2<x1+fx)):
    #         pg.draw.line(display, [5, 255, 255], (x1,y1), (x1-fx*1300,y1-fy*1300),2)
    #         vectors.append([[x1,y1],[x1-fx,y1-fy]])
    #     else:
    #         pg.draw.line(display, [5, 255, 255], (x1, y1), (x1 + fx*1300, y1 + fy*1300), 2)
    #         vectors.append([[x1, y1], [x1 + fx, y1 + fy]])
    #
    #     total += 1

    resulting_vector = [[0,0],[0,0]]
    for vector in vectors:
        resulting_vector[0][0] += vector[0][0]
        resulting_vector[0][1] += vector[0][1]
        resulting_vector[1][0] += vector[1][0]
        resulting_vector[1][1] += vector[1][1]

    if(len(vectors)>0):
        resulting_vector[0][0] = resulting_vector[0][0]/len(vectors)
        resulting_vector[0][1] = resulting_vector[0][1] / len(vectors)
        resulting_vector[1][0] = resulting_vector[1][0] / len(vectors)
        resulting_vector[1][1] = resulting_vector[1][1] / len(vectors)

    # print('resulting ', resulting_vector[0], resulting_vector[1])
    pg.draw.line(display, [5, 5, 255], resulting_vector[0], resulting_vector[1], 2)
    return (resulting_vector[0],resulting_vector[1], position)

loop = True
cont2 = 0
center_coordinates = [[6,1.4], [1.4, 1.4], [6,6], [2,2], [1.4,6]]
center_coordinates_pointer = 0
angles = [60,120,180,240,300,360,330,300,270,240,210,180,150,120,90,60,30]
angle_pointer = 0

number_of_balls = 8
while loop:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            loop = False
    # rectangle = pg.Rect(50, 50, 15, 15)
    # pg.draw.rect(display, [255, 255, 255, 255], rectangle)

    x = 100
    y = 100
    if(len(coordinates) == 0 and len(coordinates_square) == 0):
        initialize_universe(9,2,2,60)
    else:
        # if (cont2 % 10000 == 0):
            # display.fill([0, 0, 0])
            # print(center_coordinates_pointer)
            # initialize_universe(number_of_balls, center_coordinates[center_coordinates_pointer][0], center_coordinates[center_coordinates_pointer][1], angles[angle_pointer])
            # if(center_coordinates_pointer == len(center_coordinates)-1):
            #     center_coordinates_pointer = 0
            #     number_of_balls += 1
            # else:
            #     center_coordinates_pointer += 1
            # if (angle_pointer == len(angles) - 1):
            #     angle_pointer = 0
            # else:
            #     angle_pointer += 1
        if(cont2<900000000000):
            display.fill([0, 0, 0])
            coordinates2 = []
            cont2 += 1
            if (cont2 % 800 == 0):
                create_circle()

            if (cont2 % 12000 == 0):
                if(len(coordinates_square)>0):
                    coordinates_square.pop(0)

            for coord in coordinates:
                a, b, position = calculate_resulting_point(coord[0], coord[1])
                # print((b[0]),coord[1]+(b[1]))
                draw_circle((b[0]),(b[1]),10)
                coordinates2.append([b[0], b[1]])
            # print()
            coordinates = coordinates2
            create_square()
            coordinates_square2 = []
            for coordinate_square in coordinates_square:
                a, b, position = calculate_square_resulting_point(coordinate_square[0], coordinate_square[1])
                pg.draw.rect(display,(26, 173, 255,255),pg.Rect(b[0], b[1], 30, 30), 0)
                coordinates_square2.append([b[0], b[1]])
            coordinates_square = coordinates_square2
    pg.display.update()

print("done")