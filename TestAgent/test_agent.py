import json
import logging
import pdb
from confluent_kafka import Consumer, Producer, KafkaException
from .cmd_handler import GetAllTests, RunTest, AbortTest, TestStatus, RunLoopTest, RunTestPlan

logger = logging.getLogger("TestAgent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

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

#pdb.set_trace() #for code debugging purposes

class TestAgent:
    def __init__(self):
        logger.info("Initializing TestAgent...") 
        self.consumer = Consumer(KAFKA_CONFIG["consumer"])
        logger.info("Kafka Consumer created with config: %s", KAFKA_CONFIG["consumer"])  # 🔹
        self.producer = Producer(KAFKA_CONFIG["producer"])
        logger.info("Kafka Producer created with config: %s", KAFKA_CONFIG["producer"])  # 🔹
        self.consumer.subscribe([REQUEST_TOPIC])
        logger.info("Subscribed to topic: %s", REQUEST_TOPIC)

    def start(self):
        logger.info("TestAgent started, listening for commands...")
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
                try:
                    command = json.loads(msg.value().decode("utf-8"))
                    self._process_command(command)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in message")
                except Exception as e:
                    logger.error("Unexpected error processing message")

        except KeyboardInterrupt:
            logger.info("Shutting down TestAgent...")
        finally:
            logger.info("Closing Kafka consumer and flushing producer...")
            self.consumer.close()
            self.producer.flush(timeout=10)  # Ensure all pending messages are delivered
            logger.info("Agent shut down cleanly.")

    def _process_command(self, command: dict):
        """Process a single command and send back a response"""
        logger.info("Processing command...")
        cmd_type = command.get("command")  # "RunTest"
        data = command.get("data", {})     
        test_id = command.get("testId", "unknown")  

        try:
            handler = COMMAND_HANDLERS.get(cmd_type)
            if not handler:
                raise ValueError(f"Unknown command type: {cmd_type}")

            #testResult = handler(data)

            response = {
                "test_id": test_id,
                "type": f"{cmd_type}Reply",
                "testStatus": "TestFail",
                "data": "dummyTestResults",
            }
            logger.info("Generated success response: %s", response)
        except Exception as e:
            logger.error(f"Error handling command {cmd_type} (request_id={test_id})")
            response = {
                "request_id": test_id,
                "agentStatus": "AgentError",
                "AgentError": str(e),
            }
            logger.info("Generated error response: %s", response)

        # Always send response
        
        #pdb.set_trace() #for code debugging purposes

        if response.get("testStatus") == "TestSuccess":
            logger.info(f"Test {test_id} completed successfully, sending reply...")
            self.producer.produce(
                REPLY_TOPIC,
                key=str(test_id),
                value=json.dumps(response),
                callback=self._delivery_report,
            )
        elif response.get("agentStatus") == "AgentError":
            logger.error(f"Test {test_id} failed due an Agent error {response.get("AgentError")} , not sending success reply.")
        else:
            error = "Dummy error"
            logger.warning(f"Test {test_id} failed due to test system error {error} , not sending success reply.")
            response = {
                "test_id": test_id,
                "type": "RunTestReply",
                "testStatus": "TestFail",
                "data": error,
            }
            self.producer.produce(
                REPLY_TOPIC,
                key=str(test_id),
                value=json.dumps(response),
                callback=self._delivery_report,
            )
        self.producer.poll(0)

    def _delivery_report(self, err, msg):
        """Delivery report callback executed on message delivery or failure"""
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            logger.info(f"Delivered message to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")
 

if __name__ == "__main__":
    agent = TestAgent()
    agent.start()