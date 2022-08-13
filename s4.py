import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

universes = {}

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)
    message = message.decode("utf-8")
    universe_params = message.split('#')
    universes[universe_params[0]] = [float(universe_params[1]), float(universe_params[2])]

    sum_x = 0
    sum_y = 0
    total_x = 0
    total_y = 0
    mean_x = 0
    mean_y = 0

    for universe in universes:
        cont = 0
        sum_x += universes[universe][0]
        sum_y += universes[universe][1]
        total_x += 1
        total_y += 1
        cont += 1

    mean_x = sum_x/total_x
    mean_y = sum_y/total_y

    #  Send reply back to client
    socket.send((str(mean_x)+"#"+str(mean_y)).encode())