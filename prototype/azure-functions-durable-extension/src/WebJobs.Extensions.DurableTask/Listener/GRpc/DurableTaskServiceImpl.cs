using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using DurableTask.GRpc;
using Grpc.Core;
using Microsoft.Extensions.Logging;


namespace Microsoft.Azure.WebJobs.Extensions.DurableTask.Listener.GRpc
{
    internal class DurableTaskServiceImpl : DurableTaskService.DurableTaskServiceBase
    {
        private readonly ILogger logger;
        private DurableTaskExtension config;

        public DurableTaskServiceImpl(DurableTaskExtension config, ILogger logger = null)
        {
            this.config = config;
            this.logger = logger;
        }


        public override Task<NewDurableTaskResponse> StartNew(NewDurableTaskRequest request, ServerCallContext context)
        {
            this.logger.LogInformation("gRPC request::StartNew received");

            DurableOrchestrationClientBase client = this.GetClient(request);
            client.StartNewAsync(request.FunctionName, null, null);

            NewDurableTaskResponse response = new NewDurableTaskResponse()
            {
                Id = "1",
                PurgeHistoryDeleteUri = "http://localhost/Delete/1",
                RewindPostUri = "http://localhost/Rewind/1",
                SendEventPostUri = "https://localhost/Event/1",
                StatusQueryGetUri = "https://localhost/Status/1",
                TerminatePostUri = "https://localhost/terminate/1",
            };
            this.logger.LogInformation("gRPC request::StartNew completed");

            return Task.FromResult(response);
        }

        protected virtual DurableOrchestrationClientBase GetClient(NewDurableTaskRequest request)
        {
            var attribute = new OrchestrationClientAttribute()
            {
                TaskHub = "DurableTask01",
            };

            return this.GetClient(attribute);
        }

        // protected virtual to allow mocking in unit tests.
        protected virtual DurableOrchestrationClientBase GetClient(OrchestrationClientAttribute attribute)
        {
            return this.config.GetClient(attribute);
        }

    }
}
