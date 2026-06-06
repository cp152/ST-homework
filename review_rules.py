from typing import Dict, Any, List


# =========================================================
# Coverage Evaluation
# =========================================================

def evaluate_coverage(line_cov: float) -> str:
    """
    根据行覆盖率评估覆盖充分性等级

    Returns:
        INSUFFICIENT
        ADEQUATE
        GOOD
        EXCELLENT
    """

    if line_cov < 0.5:
        return "INSUFFICIENT"

    if line_cov < 0.8:
        return "ADEQUATE"

    if line_cov < 0.9:
        return "GOOD"

    return "EXCELLENT"


# =========================================================
# Assertion Quality Estimation
# =========================================================

def estimate_assertion_quality(
        assertion_count: int,
        has_assertion_message: bool,
        uses_assert_throws: bool
) -> float:
    """
    粗略估计断言质量

    返回范围:
        0.0 ~ 1.0
    """

    score = 0.0

    # 存在断言
    if assertion_count > 0:
        score += 0.5

    # 存在 assertion message
    if has_assertion_message:
        score += 0.25

    # 正确使用 assertThrows
    if uses_assert_throws:
        score += 0.25

    return min(score, 1.0)


# =========================================================
# Quality Score Calculation
# =========================================================

def calculate_quality_score(
        line_cov: float,
        branch_cov: float,
        assertion_quality: float
) -> float:
    """
    综合质量评分

    Formula:
        0.4 * lineCoverage
      + 0.4 * branchCoverage
      + 0.2 * assertionQuality
    """

    score = (
            0.4 * line_cov
            + 0.4 * branch_cov
            + 0.2 * assertion_quality
    )

    return round(min(max(score, 0.0), 1.0), 2)


# =========================================================
# Compile Status Check
# =========================================================

def is_compile_success(execution_report: Dict[str, Any]) -> bool:
    """
    判断编译是否成功
    """

    compile_result = execution_report.get("compileResult", {})
    return compile_result.get("success", False)


# =========================================================
# Failed Test Count
# =========================================================

def get_failed_test_count(execution_report: Dict[str, Any]) -> int:
    """
    获取失败测试数量
    """

    execution_results = execution_report.get("executionResults")

    if not execution_results:
        return 0

    failed = execution_results.get("failed", 0)
    errors = execution_results.get("errors", 0)

    return failed + errors


# =========================================================
# High Severity Issue Count
# =========================================================

def count_high_severity_issues(
        issue_details: List[Dict[str, Any]]
) -> int:
    """
    统计 HIGH 严重级别 issue 数量
    """

    count = 0

    for issue in issue_details:
        if issue.get("severity") == "HIGH":
            count += 1

    return count


# =========================================================
# Iteration Decision
# =========================================================

def should_continue(
        line_cov: float,
        branch_cov: float,
        target_line_cov: float,
        target_branch_cov: float,
        compile_success: bool,
        failed_test_count: int,
        high_severity_issue_count: int
) -> bool:
    """
    判断是否继续迭代

    Continue if:
    1. 覆盖率未达标
    2. 编译失败
    3. 测试失败
    4. 存在 HIGH issue
    """

    # 编译失败
    if not compile_success:
        return True

    # 存在测试失败
    if failed_test_count > 0:
        return True

    # 存在高严重性问题
    if high_severity_issue_count > 0:
        return True

    # 覆盖率不足
    if line_cov < target_line_cov:
        return True

    if branch_cov < target_branch_cov:
        return True

    return False


# =========================================================
# Focus Area Generation
# =========================================================

def generate_focus_areas(
        line_cov: float,
        branch_cov: float,
        failed_test_count: int,
        high_severity_issue_count: int
) -> List[str]:
    """
    生成下一轮优化重点
    """

    focus_areas = []

    # 行覆盖率低
    if line_cov < 0.8:
        focus_areas.append("Line coverage improvement")

    # 分支覆盖率低
    if branch_cov < 0.7:
        focus_areas.append("Branch path testing")

    # 测试失败
    if failed_test_count > 0:
        focus_areas.append("Assertion enhancement")

    # 高严重性问题
    if high_severity_issue_count > 0:
        focus_areas.append("Exception handling")

    # 默认边界值测试
    if len(focus_areas) == 0:
        focus_areas.append("Boundary value testing")

    return focus_areas


# =========================================================
# Normative Level Evaluation
# =========================================================

def evaluate_normative_level(
        assertion_quality: float
) -> str:
    """
    评估测试规范等级
    """

    if assertion_quality < 0.4:
        return "POOR"

    if assertion_quality < 0.7:
        return "ACCEPTABLE"

    if assertion_quality < 0.9:
        return "GOOD"

    return "EXCELLENT"


# =========================================================
# Overall Assessment Builder
# =========================================================

def build_overall_assessment(
        line_cov: float,
        branch_cov: float,
        assertion_quality: float
) -> Dict[str, Any]:
    """
    构建 overallAssessment
    """

    quality_score = calculate_quality_score(
        line_cov,
        branch_cov,
        assertion_quality
    )

    coverage_adequacy = evaluate_coverage(line_cov)

    normative_level = evaluate_normative_level(
        assertion_quality
    )

    summary = (
        f"Line coverage={line_cov:.2f}, "
        f"branch coverage={branch_cov:.2f}, "
        f"overall quality score={quality_score:.2f}."
    )

    return {
        "qualityScore": quality_score,
        "coverageAdequacy": coverage_adequacy,
        "normativeLevel": normative_level,
        "summary": summary
    }
