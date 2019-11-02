using System;
using System.Net.Http;
using System.Threading.Tasks;
using DotNetGrpcService;
using Grpc.Net.Client;

namespace DotNetGrpcClient
{
 class Program
    {
        static async Task Main(string[] args)
        {
            // The port number(5001) must match the port of the gRPC server.

            Console.WriteLine("Calling C# Endpoint...");
            await CallEndpoint("http://localhost:5000", true);

            Console.WriteLine("Calling Python Endpoint...");
            await CallEndpoint("http://localhost:50051", true);
            
        }

        static GrpcChannel GetChannel(string grpcEndpointAddress, bool isInsecure = false)
        {
            AppContext.SetSwitch("System.Net.Http.SocketsHttpHandler.Http2UnencryptedSupport", isInsecure);
            return GrpcChannel.ForAddress(grpcEndpointAddress);           
        }

        static async Task CallEndpoint(string grpcEndpointAddress, bool isInsecure = false)
        {
            var channel = GetChannel(grpcEndpointAddress, isInsecure);
            var client = new Greeter.GreeterClient(channel);

            var reply = await client.SayHelloAsync(
                              new HelloRequest { Name = "GreeterClient-DotNet" });
            Console.WriteLine($"Response: {reply.Message}");
        }
    }
}
