from concurrent import futures
import grpc

import greet_pb2_grpc
import greet_pb2

class GreetServer (greet_pb2_grpc.GreeterServicer):
    
    def SayHello(self, request, context):
        return greet_pb2.HelloReply(message='Hello ' + request.name)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreetServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':    
    serve()