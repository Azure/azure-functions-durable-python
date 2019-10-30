import grpc

import greet_pb2_grpc
import greet_pb2



def getChannel(grpcEndpointAddress):
    return grpc.insecure_channel(grpcEndpointAddress)

def sendGreetings(grpcChannel):
    stub = greet_pb2_grpc.GreeterStub(grpcChannel)
    reply = stub.SayHello(greet_pb2.HelloRequest(name='Shashank'))
    return reply

def main():    
    print ("Send greetings to C# Server...")
    channel = getChannel("localhost:5000")
    print(sendGreetings(channel))

    print ("Send greetings to Python Server...")
    channel = getChannel("localhost:50051")
    print(sendGreetings(channel))

if __name__ == '__main__':    
    main()
