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
     
            return base.StartNew(request, context);
        }

    }
}
