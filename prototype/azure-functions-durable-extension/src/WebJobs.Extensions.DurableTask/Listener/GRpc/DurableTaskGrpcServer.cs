using DurableTask.GRpc;
using Grpc.Core;
using Microsoft.Extensions.Logging;

namespace Microsoft.Azure.WebJobs.Extensions.DurableTask.Listener.GRpc
{
 
    internal class DurableTaskGrpcServer
    {
        private const int DefaultgRPCPort = 50051;

        private int serverPort;

        private Server grpcServer;

        private DurableTaskExtension config;
        private ILogger logger;


        public DurableTaskGrpcServer(DurableTaskExtension config, ILogger logger)
        {
            this.config = config;
            this.logger = logger;
        }

        public void StartServer(int serverPort = DefaultgRPCPort)
        {
            this.serverPort = serverPort;

            this.grpcServer = new Server
            {
                Services = { DurableTaskService.BindService(new DurableTaskServiceImpl(this.config, this.logger)) },
                Ports = { new ServerPort("localhost", this.serverPort, ServerCredentials.Insecure) },
            };

            this.logger.LogInformation($"Starting Durable Task - gRPC server on - {this.serverPort}");

            this.grpcServer.Start();
            
        }
    }
}
