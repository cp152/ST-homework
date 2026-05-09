import uuid
from datetime import datetime, timezone


def generate_uuid():
    return str(uuid.uuid4())


def current_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def execute(test_case_msg):

    return {

        "sourceCodeLoc":
            "./source1.java",

        "protocolVersion":
            "1.0",

        "messageId":
            generate_uuid(),

        "sessionId":
            test_case_msg["sessionId"],

        "parentMessageId":
            test_case_msg["messageId"],

        "timestamp":
            current_timestamp(),

        "messageType":
            "ExecutionReport",

        "sourceClassName":
            test_case_msg["sourceClassName"],

        "testClassName":
            test_case_msg["testClassName"],

        "executionStatus":
            "SUCCESS",

        "environmentCompatibility": {
            "isCompatible": True,
            "mismatches": []
        },

        "compileResult": {
            "success": True,
            "errors": []
        },

        "executionResults": {
            "totalMethods": 5,
            "passed": 4,
            "failed": 1,
            "errors": 0,
            "details": []
        },

        "coverage": {
            "lineCoverage": 0.65,
            "branchCoverage": 0.50,
            "methodCoverage": 0.75,
            "uncoveredItems": []
        },

        "environment": {
            "javaVersion": "17",
            "junitVersion": "5.9.3",
            "mockFramework": "Mockito"
        }
    }
