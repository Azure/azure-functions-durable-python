import grpc

import greet_pb2_grpc
import greet_pb2


def getChannel(grpcEndpointAddress):
    return grpc.insecure_channel(grpcEndpointAddress)


def sendGreetings(grpcChannel):
    stub = greet_pb2_grpc.GreeterStub(grpcChannel)
    reply = stub.SayHello(greet_pb2.HelloRequest(name='GreeterClient-Python'))
    return reply.message


def main():
    print("Calling C# Endpoint...")
    channel = getChannel("localhost:5000")
    print(f'Response: {sendGreetings(channel)}')

    print("Calling Python Endpoint...")
    channel = getChannel("localhost:50051")
    print(f'Response: {sendGreetings(channel)}')


if __name__ == '__main__':
    main()
