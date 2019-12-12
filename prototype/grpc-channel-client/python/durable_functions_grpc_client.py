import grpc

import DurableFunctions_pb2_grpc
import DurableFunctions_pb2


def get_channel(grpcEndpointAddress):
    return grpc.insecure_channel(grpcEndpointAddress)


def start_new(grpcChannel):
    stub = DurableFunctions_pb2_grpc.DurableTaskServiceStub(grpcChannel)
    reply = stub.StartNew(DurableFunctions_pb2.NewDurableTaskRequest(functionName="HelloWorld"))
    return reply


def main():
    channel = get_channel("localhost:50051")
    start_new(channel)


if __name__ == '__main__':
    main()
