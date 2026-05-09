import uuid
from datetime import datetime, timezone


def generate_uuid():
    return str(uuid.uuid4())


def current_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def generate(
        class_name,
        class_description,
        iteration,
        previous_feedback
):

    return {

        "sourceCodeLoc":
            "./source1.java",

        "protocolVersion":
            "1.0",

        "messageId":
            generate_uuid(),

        "sessionId":
            previous_feedback["sessionId"],

        "parentMessageId":
            previous_feedback["messageId"],

        "timestamp":
            current_timestamp(),

        "messageType":
            "GeneratedTestCase",

        "sourceClassName":
            class_name,

        "sourceVersion":
            "sha256-demo",

        "testClassName":
            f"{class_name}Test",

        "testCodeLoc":
            "./CalculatorTest.java",

        "requiredEnvironment": {
            "junitVersion": "5.9.3",
            "javaVersion": "17"
        },

        "targetCoverage": {
            "lineCoverage": 0.8,
            "branchCoverage": 0.7,
            "methodCoverage": 0.75
        }
    }
