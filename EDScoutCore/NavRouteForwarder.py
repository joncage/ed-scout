import time
import eventlet.green.zmq as zmq

class Sender:

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = self.socket.bind_to_random_port("tcp://*")


    def send(self, message):
        self.socket.send_string(message)


class Receiver:

    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:"+str(port))
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")  # b"" allows us to receive all

    def receive(self):
        return self.socket.recv()


if __name__ == '__main__':
    r = Receiver()
    print("receiving..")
    print(r.receive())

