# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import DurableFunctions_pb2 as DurableFunctions__pb2


class DurableTaskServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.StartNew = channel.unary_unary(
        '/gRPCChannel.DurableTaskService/StartNew',
        request_serializer=DurableFunctions__pb2.NewDurableTaskRequest.SerializeToString,
        response_deserializer=DurableFunctions__pb2.NewDurableTaskResponse.FromString,
        )


class DurableTaskServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def StartNew(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DurableTaskServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'StartNew': grpc.unary_unary_rpc_method_handler(
          servicer.StartNew,
          request_deserializer=DurableFunctions__pb2.NewDurableTaskRequest.FromString,
          response_serializer=DurableFunctions__pb2.NewDurableTaskResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'gRPCChannel.DurableTaskService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
