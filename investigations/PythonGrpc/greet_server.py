from concurrent import futures
import grpc

import greet_pb2_grpc
import greet_pb2


class GreetServer (greet_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        print(f'Received client request from {request.name}')
        return greet_pb2.HelloReply(message=f'Hello {request.name} from Python gRPC Server')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreetServer(), server)
    print('Starting gRPC Server on port 50051')
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Started. Waiting for client connections...')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
