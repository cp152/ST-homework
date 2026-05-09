import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from review_rules import *


# =========================================================
# Utility Functions
# =========================================================

def generate_uuid() -> str:
    return str(uuid.uuid4())


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_test_code(test_code_loc: str) -> str:
    """
    读取测试代码
    """

    try:
        with open(test_code_loc, "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return ""


# =========================================================
# Issue Generation
# =========================================================

def generate_issue_details(
        execution_report: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    根据 execution report 生成 issue 列表
    """

    issues = []

    coverage = execution_report.get("coverage", {})

    line_cov = coverage.get("lineCoverage", 0.0)
    branch_cov = coverage.get("branchCoverage", 0.0)

    execution_results = execution_report.get(
        "executionResults",
        {}
    )

    failed_tests = execution_results.get("failed", 0)
    errors = execution_results.get("errors", 0)

    # =====================================================
    # Coverage Gap
    # =====================================================

    if branch_cov < 0.7:
        issues.append({
            "issueId": generate_uuid(),
            "category": "COVERAGE_GAP",
            "severity": "HIGH",
            "targetMethod": "UNKNOWN",
            "description": "Branch coverage is insufficient.",
            "relatedCoverageItemId": None,
            "suggestion": "Add additional branch path tests."
        })

    # =====================================================
    # Assertion Problems
    # =====================================================

    if failed_tests > 0:
        issues.append({
            "issueId": generate_uuid(),
            "category": "ASSERTION",
            "severity": "MEDIUM",
            "targetMethod": "UNKNOWN",
            "description": "Some test assertions failed.",
            "relatedCoverageItemId": None,
            "suggestion": "Check expected values and assertion logic."
        })

    # =====================================================
    # Execution Errors
    # =====================================================

    if errors > 0:
        issues.append({
            "issueId": generate_uuid(),
            "category": "EXCEPTION_HANDLING",
            "severity": "HIGH",
            "targetMethod": "UNKNOWN",
            "description": "Unexpected runtime errors exist.",
            "relatedCoverageItemId": None,
            "suggestion": "Add exception handling test cases."
        })

    # =====================================================
    # Low Line Coverage
    # =====================================================

    if line_cov < 0.8:
        issues.append({
            "issueId": generate_uuid(),
            "category": "EDGE_CASE",
            "severity": "MEDIUM",
            "targetMethod": "UNKNOWN",
            "description": "Line coverage is below target.",
            "relatedCoverageItemId": None,
            "suggestion": "Add boundary value and edge-case tests."
        })

    return issues


# =========================================================
# Build ReviewFeedback
# =========================================================

def build_review_feedback(
        execution_report: Dict[str, Any],
        issue_details: List[Dict[str, Any]],
        overall_assessment: Dict[str, Any],
        should_continue_flag: bool,
        focus_areas: List[str]
) -> Dict[str, Any]:
    """
    构建最终 ReviewFeedback JSON
    """

    coverage = execution_report.get("coverage", {})

    return {

        "sourceCodeLoc":
            execution_report.get("sourceCodeLoc"),

        "protocolVersion":
            "1.0",

        "messageId":
            generate_uuid(),

        "sessionId":
            execution_report.get("sessionId"),

        "parentMessageId":
            execution_report.get("messageId"),

        "timestamp":
            current_timestamp(),

        "messageType":
            "ReviewFeedback",

        "sourceClassName":
            execution_report.get("sourceClassName"),

        "testClassName":
            execution_report.get("testClassName"),

        "overallAssessment":
            overall_assessment,

        "issueDetails":
            issue_details,

        "iterationAdvice": {

            "shouldContinue":
                should_continue_flag,

            "focusArea":
                focus_areas,

            "targetNextCoverage": {

                "lineCoverage":
                    min(
                        coverage.get("lineCoverage", 0.0) + 0.1,
                        1.0
                    ),

                "branchCoverage":
                    min(
                        coverage.get("branchCoverage", 0.0) + 0.1,
                        1.0
                    ),

                "methodCoverage":
                    min(
                        coverage.get("methodCoverage", 0.0) + 0.1,
                        1.0
                    )
            }
        }
    }


# =========================================================
# Main Review Function
# =========================================================

def review(
        execution_report: Dict[str, Any],
        test_code_loc: str
) -> Dict[str, Any]:

    print("========== Reviewer Agent ==========")

    # =====================================================
    # 1. Read Coverage Info
    # =====================================================

    coverage = execution_report.get("coverage", {})

    line_cov = coverage.get("lineCoverage", 0.0)

    branch_cov = coverage.get("branchCoverage", 0.0)

    # =====================================================
    # 2. Load Test Code
    # =====================================================

    test_code = load_test_code(test_code_loc)

    print(f"Loaded test code length: {len(test_code)}")

    # =====================================================
    # 3. Estimate Assertion Quality
    # =====================================================

    assertion_quality = estimate_assertion_quality(
        assertion_count=3,
        has_assertion_message=True,
        uses_assert_throws=False
    )

    # =====================================================
    # 4. Generate Overall Assessment
    # =====================================================

    overall_assessment = build_overall_assessment(
        line_cov,
        branch_cov,
        assertion_quality
    )

    # =====================================================
    # 5. Generate Issues
    # =====================================================

    issue_details = generate_issue_details(
        execution_report
    )

    # =====================================================
    # 6. Count High Severity Issues
    # =====================================================

    high_issue_count = count_high_severity_issues(
        issue_details
    )

    # =====================================================
    # 7. Compile Status
    # =====================================================

    compile_success = is_compile_success(
        execution_report
    )

    # =====================================================
    # 8. Failed Test Count
    # =====================================================

    failed_test_count = get_failed_test_count(
        execution_report
    )

    # =====================================================
    # 9. Decide Whether Continue
    # =====================================================

    continue_flag = should_continue(
        line_cov=line_cov,
        branch_cov=branch_cov,

        target_line_cov=0.9,
        target_branch_cov=0.8,

        compile_success=compile_success,

        failed_test_count=failed_test_count,

        high_severity_issue_count=high_issue_count
    )

    # =====================================================
    # 10. Generate Focus Areas
    # =====================================================

    focus_areas = generate_focus_areas(
        line_cov,
        branch_cov,
        failed_test_count,
        high_issue_count
    )

    # =====================================================
    # 11. Build Final JSON
    # =====================================================

    feedback = build_review_feedback(
        execution_report,
        issue_details,
        overall_assessment,
        continue_flag,
        focus_areas
    )

    print("Reviewer feedback generated.")

    return feedback
