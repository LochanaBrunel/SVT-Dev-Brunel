# Hard-coded topics for your requirement
REQUEST_TOPIC = "svt.test-agent.request"
REPLY_TOPIC = "svt.test-agent.request.reply"

# Kafka config – change bootstrap.servers if needed
KAFKA_CONFIG = {
    "consumer": {
        "bootstrap.servers": "localhost:9095",   # if running on host
        "group.id": "test-agent",
        "auto.offset.reset": "earliest",
    },
    "producer": {
        "bootstrap.servers": "localhost:9095",
    },
}

# Mapping of command types to handlers
COMMAND_HANDLERS = {
    "GetAllTests": GetAllTests,
    "RunTest": RunTest,
    "AbortTest": AbortTest,
    "TestStatus": TestStatus,
    "RunLoopTest": RunLoopTest,
    "RunTestPlan": RunTestPlan,
}

""" 

GetAllTests: Get the list of all tests available per Chip
RunTest: Initiate a test
AbortTest: Stop a running test
TestStatus: Get the status of a running test
RunLoopTest: Run a purticular test iteratively
RunTestPlan: Run a sequence of tests 

"""