import grpc

import greet_pb2
import greet_pb2_grpc


with open('localhost.cer', 'rb') as f:
    cert= f.read()
creds = grpc.ssl_channel_credentials(cert)

channel = grpc.insecure_channel('localhost:50051')
#channel = grpc.secure_channel('localhost:5001', creds)
stub = greet_pb2_grpc.GreeterStub(channel)

greetings = stub.SayHello(greet_pb2.HelloRequest(name='Shashank'))

print(greetings)
