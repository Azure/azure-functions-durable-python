HANDLE_ONE = '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
             '{"OrchestrationInstance":{"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
             '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,"ParentInstance":null,' \
             '"Name":"DurableFunctionsOrchestratorJS","Version":"","Input":"null","Tags":null,"EventId":-1,' \
             '"IsPlayed":false,"Timestamp":"2019-12-08T23:18:39.756132Z"}],"input":null,' \
             '"instanceId":"48d0f95957504c2fa579e810a390b938","isReplaying":false,"parentInstanceId":null}'

STATE_ONE = '{"isDone":false,"actions":[[{"functionName":"Hello","input":"Tokyo","actionType":0}]]}'

HANDLE_TWO = '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
             '{"OrchestrationInstance":{"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
             '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,"ParentInstance":null,' \
             '"Name":"DurableFunctionsOrchestratorJS","Version":"","Input":"null","Tags":null,"EventId":-1,' \
             '"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39.756132Z"},{"EventType":4,"Name":"Hello","Version":"",' \
             '"Input":null,"EventId":0,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:51.5313393Z"},{"EventType":13,' \
             '"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:51.5320985Z"},{"EventType":12,"EventId":-1,' \
             '"IsPlayed":false,"Timestamp":"2019-12-08T23:29:52.4899106Z"},{"EventType":5,"TaskScheduledId":0,' \
             '"Result":"Hello Tokyo!","EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:51.7873033Z"}],' \
             '"input":null,"instanceId":"48d0f95957504c2fa579e810a390b938","isReplaying":true,"parentInstanceId":null}'

STATE_TWO = '{"isDone":false,"actions":[[{"functionName":"Hello","input":"Tokyo","actionType":0}],' \
            '[{"functionName":"Hello","input":"Seattle","actionType":0}]]}'

HANDLE_THREE = '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:18:41.3240927Z"},{"OrchestrationInstance":{' \
               '"InstanceId":"48d0f95957504c2fa579e810a390b938","ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},' \
               '"EventType":0,"ParentInstance":null,"Name":"DurableFunctionsOrchestratorJS","Version":"",' \
               '"Input":"null","Tags":null,"EventId":-1,"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39.756132Z"},' \
               '{"EventType":4,"Name":"Hello","Version":"","Input":null,"EventId":0,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:29:51.5313393Z"},{"EventType":13,"EventId":-1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:29:51.5320985Z"},{"EventType":12,"EventId":-1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:29:52.4899106Z"},{"EventType":5,"TaskScheduledId":0,"Result":"Hello ' \
               'Tokyo!","EventId":-1,"IsPlayed":true,"Timestamp":"2019-12-08T23:29:51.7873033Z"},{"EventType":4,' \
               '"Name":"Hello","Version":"","Input":null,"EventId":1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:34:12.2632487Z"},{"EventType":13,"EventId":-1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:34:12.263286Z"},{"EventType":12,"EventId":-1,"IsPlayed":false,' \
               '"Timestamp":"2019-12-08T23:34:12.8710525Z"},{"EventType":5,"TaskScheduledId":1,"Result":"Hello ' \
               'Seattle!","EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:34:12.561288Z"}],"input":null,' \
               '"instanceId":"48d0f95957504c2fa579e810a390b938","isReplaying":true,"parentInstanceId":null}'

STATE_THREE = '{"isDone":false,"actions":[[{"functionName":"Hello","input":"Tokyo","actionType":0}],' \
              '[{"functionName":"Hello","input":"Seattle","actionType":0}],[{"functionName":"Hello","input":"London",' \
              '"actionType":0}]]}'

HANDLE_FOUR = '{"history":[{"EventType":12,"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:18:41.3240927Z"},' \
              '{"OrchestrationInstance":{"InstanceId":"48d0f95957504c2fa579e810a390b938",' \
              '"ExecutionId":"fd183ee02e4b4fd18c95b773cfb5452b"},"EventType":0,"ParentInstance":null,' \
              '"Name":"DurableFunctionsOrchestratorJS","Version":"","Input":"null","Tags":null,"EventId":-1,' \
              '"IsPlayed":true,"Timestamp":"2019-12-08T23:18:39.756132Z"},{"EventType":4,"Name":"Hello","Version":"",' \
              '"Input":null,"EventId":0,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:51.5313393Z"},{"EventType":13,' \
              '"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:51.5320985Z"},{"EventType":12,' \
              '"EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:29:52.4899106Z"},{"EventType":5,' \
              '"TaskScheduledId":0,"Result":"Hello Tokyo!","EventId":-1,"IsPlayed":true,' \
              '"Timestamp":"2019-12-08T23:29:51.7873033Z"},{"EventType":4,"Name":"Hello","Version":"","Input":null,' \
              '"EventId":1,"IsPlayed":false,"Timestamp":"2019-12-08T23:34:12.2632487Z"},{"EventType":13,"EventId":-1,' \
              '"IsPlayed":false,"Timestamp":"2019-12-08T23:34:12.263286Z"},{"EventType":12,"EventId":-1,' \
              '"IsPlayed":false,"Timestamp":"2019-12-08T23:34:12.8710525Z"},{"EventType":5,"TaskScheduledId":1,' \
              '"Result":"Hello Seattle!","EventId":-1,"IsPlayed":true,"Timestamp":"2019-12-08T23:34:12.561288Z"},' \
              '{"EventType":4,"Name":"Hello","Version":"","Input":null,"EventId":2,"IsPlayed":false,' \
              '"Timestamp":"2019-12-08T23:35:01.5011494Z"},{"EventType":13,"EventId":-1,"IsPlayed":false,' \
              '"Timestamp":"2019-12-08T23:35:01.5011554Z"},{"EventType":12,"EventId":-1,"IsPlayed":false,' \
              '"Timestamp":"2019-12-08T23:36:20.866617Z"},{"EventType":5,"TaskScheduledId":2,"Result":"Hello ' \
              'London!","EventId":-1,"IsPlayed":false,"Timestamp":"2019-12-08T23:36:20.5364383Z"}],"input":null,' \
              '"instanceId":"48d0f95957504c2fa579e810a390b938","isReplaying":true,"parentInstanceId":null} '

STATE_FOUR = '{"isDone":true,"actions":[[{"functionName":"Hello","input":"Tokyo","actionType":0}],' \
             '[{"functionName":"Hello","input":"Seattle","actionType":0}],[{"functionName":"Hello","input":"London",' \
             '"actionType":0}]],"output":["Hello Tokyo!","Hello Seattle!","Hello London!"]} '
