import json
def review(x,y,z):
    return {
        "protocolVersion": "1.0",
        "messageId": "123e4567-e89b-12d3-a456-426614174003",
        "sessionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "parentMessageId": "ExecutionReport的messageId",
        "timestamp": "2026-05-06T10:30:15Z",
        "messageType": "ReviewFeedback",
        "sourceClassName": "com.example.Calculator",
        "testClassName": "com.example.CalculatorTest",
        "overallAssessment": {
            "qualityScore": 0.6,
            "coverageAdequacy": "INSUFFICIENT",
            "normativeLevel": "ACCEPTABLE",
            "summary": "测试逻辑基本合理，但缺少对 null 参数、溢出等边界场景的覆盖，断言消息缺失。"
        },
        "issueDetails": [
            {
            "issueId": "issue-001",
            "category": "COVERAGE_GAP",
            "severity": "HIGH",
            "targetMethod": "add",
            "description": "未测试两个整数相加溢出的情况。",
            "relatedCoverageItemId": "cov-003",
            "suggestion": "增加测试用例 testAdd_Overflow，传入 Integer.MAX_VALUE 和 1，验证抛出 ArithmeticException 或返回预期溢出结果。"
            },
            {
            "issueId": "issue-002",
            "category": "ASSERTION",
            "severity": "MEDIUM",
            "targetMethod": "testSubtract_NegativeResult",
            "description": "断言缺少失败时的提示消息，难以快速定位问题。",
            "suggestion": "使用 assertEquals( -5, result, \"subtract(2,7) should return -5\" );"
            },
            {
            "issueId": "issue-003",
            "category": "CODE_STYLE",
            "severity": "LOW",
            "targetMethod": "testAdd_PositiveNumbers",
            "description": "方法名未遵循 givenWhenThen 模式，可读性一般。",
            "suggestion": "重命名为 testAdd_givenPositiveNumbers_returnsSum"
            }
        ],
        "iterationAdvice": {
            "shouldContinue": True,
            "focusArea": ["边界值测试", "异常场景覆盖", "断言描述"],
            "targetNextCoverage": {
            "lineCoverage": 0.85,
            "branchCoverage": 0.75,
            "methodCoverage": 0.75,
            }
        }
    }