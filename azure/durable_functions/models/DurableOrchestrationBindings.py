from typing import Dict


class DurableOrchestrationBindings:
    def __init__(self):
        self.taskHubName: str
        self.creationUrls: Dict[str, str]
        self.managementUrls: Dict[str, str]

'''
"taskHubName":"DurableFunctionsHub",
"creationUrls":{
    "createNewInstancePostUri":"http://localhost:7071/runtime/webhooks/durabletask/orchestrators/{functionName}[/{instanceId}]?code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg==",
    "createAndWaitOnNewInstancePostUri":"http://localhost:7071/runtime/webhooks/durabletask/orchestrators/{functionName}[/{instanceId}]?timeout={timeoutInSeconds}&pollingInterval={intervalInSeconds}&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg=="
},
"managementUrls":{
    "id":"INSTANCEID",
    "statusQueryGetUri":"http://localhost:7071/runtime/webhooks/durabletask/instances/INSTANCEID?taskHub=DurableFunctionsHub&connection=Storage&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg==",
    "sendEventPostUri":"http://localhost:7071/runtime/webhooks/durabletask/instances/INSTANCEID/raiseEvent/{eventName}?taskHub=DurableFunctionsHub&connection=Storage&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg==",
    "terminatePostUri":"http://localhost:7071/runtime/webhooks/durabletask/instances/INSTANCEID/terminate?reason={text}&taskHub=DurableFunctionsHub&connection=Storage&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg==",
    "rewindPostUri":"http://localhost:7071/runtime/webhooks/durabletask/instances/INSTANCEID/rewind?reason={text}&taskHub=DurableFunctionsHub&connection=Storage&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg==",
    "purgeHistoryDeleteUri":"http://localhost:7071/runtime/webhooks/durabletask/instances/INSTANCEID?taskHub=DurableFunctionsHub&connection=Storage&code=GBgDKQriGLABxpY/m5qcPd3R2sNafdRPE3/LcUSZEnuvOzTA1qD3Tg=="
}
'''