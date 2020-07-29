import time
import eventlet.green.zmq as zmq

class Sender:

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")

    def send(self, message):
        self.socket.send_string(message)


class Receiver:

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5555")
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")  # b"" allows us to receive all

    def receive(self):
        return self.socket.recv()


if __name__ == '__main__':
    r = Receiver()
    print("receiving..")
    print(r.receive())

