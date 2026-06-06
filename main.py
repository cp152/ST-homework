import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import traceback

# 引入三个模型（假设它们已实现，以下为占位）
try:
    from examiner import generate as examiner_generate
    from solver import execute as solver_execute
    from reviewer import review as reviewer_review
except ImportError:
    def examiner_generate(source_code_loc: str, class_name: str, class_description: str,
                      iteration: int, previous_feedback: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("出题人模型未实现")

    def solver_execute(test_case_msg: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("解题人模型未实现")

    def reviewer_review(execution_report: Dict[str, Any], test_code_loc: str) -> Dict[str, Any]:
        raise NotImplementedError("评审员模型未实现")


# ================== 工具函数 ==================
def generate_uuid() -> str:
    """生成符合UUID标准的字符串"""
    return str(uuid.uuid4())


def current_iso_timestamp() -> str:
    """返回当前UTC时间的ISO 8601格式字符串"""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def build_message_header(source_code_loc: str, message_type: str, parent_id: Optional[str] = None,
                         session_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "sourceCodeLoc": source_code_loc,
        "protocolVersion": "1.0",
        "messageId": generate_uuid(),
        "sessionId": session_id if session_id else generate_uuid(),
        "parentMessageId": parent_id,
        "timestamp": current_iso_timestamp(),
        "messageType": message_type
    }


# ================== 格式验证 ==================
# 以下为基于关键字段的轻量级验证，可扩展为完整 JSON Schema 校验
def validate_required_fields(obj: Dict[str, Any], required_fields: List[str],
                             context: str) -> None:
    """验证字典中必须包含某些非空字段"""
    for field in required_fields:
        if field not in obj or obj[field] is None:
            raise ValueError(f"{context} 缺少必需字段: {field}")


def validate_generated_test_case(msg: Dict[str, Any]) -> None:
    """验证出题人输出是否符合 2.1 规范"""
    required = ["sourceCodeLoc", "protocolVersion", "messageId", "sessionId", "parentMessageId",
                "timestamp", "messageType", "sourceClassName", "testClassName",
                "testCodeLoc", "requiredEnvironment", "targetCoverage"]
    validate_required_fields(msg, required, "GeneratedTestCase")
    if msg["messageType"] != "GeneratedTestCase":
        raise ValueError("messageType 应为 GeneratedTestCase")
    env = msg["requiredEnvironment"]
    if "junitVersion" not in env or "javaVersion" not in env:
        raise ValueError("requiredEnvironment 缺少 junitVersion 或 javaVersion")
    cov = msg["targetCoverage"]
    for key in ["lineCoverage", "branchCoverage", "methodCoverage"]:
        if key in cov and not (0.0 <= cov[key] <= 1.0):
            raise ValueError(f"targetCoverage.{key} 取值范围应为 [0,1]")
    file_path = msg["testCodeLoc"]
    if not os.path.exists(file_path):
        raise  ValueError(f"测试代码：{file_path} 不存在")


def validate_execution_report(msg: Dict[str, Any]) -> None:
    """验证解题人输出是否符合 2.2 规范"""
    required = ["sourceCodeLoc", "protocolVersion", "messageId", "sessionId", "parentMessageId",
                "timestamp", "messageType", "sourceClassName", "testClassName",
                "executionStatus", "environmentCompatibility", "compileResult",
                "environment"]
    validate_required_fields(msg, required, "ExecutionReport")
    if msg["messageType"] != "ExecutionReport":
        raise ValueError("messageType 应为 ExecutionReport")
    status = msg["executionStatus"]
    # 根据状态检查其他字段的存在性
    if status in ["COMPILATION_ERROR", "ENVIRONMENT_MISMATCH", "SYSTEM_ERROR", "TIMEOUT"]:
        if msg.get("executionResults") is not None:
            raise ValueError(f"当 executionStatus={status} 时，executionResults 必须为 null")
        if msg.get("coverage") is not None:
            raise ValueError(f"当 executionStatus={status} 时，coverage 必须为 null")
    else:
        if "executionResults" not in msg or msg["executionResults"] is None:
            raise ValueError("executionResults 不能为 null")
        if "coverage" not in msg or msg["coverage"] is None:
            raise ValueError("coverage 不能为 null")
    # 校验覆盖率为 [0,1] 小数
    cov = msg.get("coverage")
    if cov:
        for key in ["lineCoverage", "branchCoverage", "methodCoverage"]:
            if key in cov and not (0.0 <= cov[key] <= 1.0):
                raise ValueError(f"coverage.{key} 取值范围应为 [0,1]")


def validate_review_feedback(msg: Dict[str, Any]) -> None:
    """验证评审员输出是否符合 2.3 规范"""
    required = ["sourceCodeLoc", "protocolVersion", "messageId", "sessionId", "parentMessageId",
                "timestamp", "messageType", "sourceClassName", "testClassName",
                "overallAssessment", "issueDetails", "iterationAdvice"]
    validate_required_fields(msg, required, "ReviewFeedback")
    if msg["messageType"] != "ReviewFeedback":
        raise ValueError("messageType 应为 ReviewFeedback")
    assess = msg["overallAssessment"]
    if "qualityScore" not in assess or not (0.0 <= assess["qualityScore"] <= 1.0):
        raise ValueError("overallAssessment.qualityScore 需在 [0,1] 范围内")
    if "coverageAdequacy" not in assess:
        raise ValueError("overallAssessment 缺少 coverageAdequacy")
    if "normativeLevel" not in assess:
        raise ValueError("overallAssessment 缺少 normativeLevel")
    advice = msg["iterationAdvice"]
    if "shouldContinue" not in advice or not isinstance(advice["shouldContinue"], bool):
        raise ValueError("iterationAdvice.shouldContinue 必须为布尔型")
    # targetNextCoverage 可选，如果有则检查覆盖率范围
    target_cov = advice.get("targetNextCoverage")
    if target_cov:
        for key in ["lineCoverage", "branchCoverage", "methodCoverage"]:
            if key in target_cov and not (0.0 <= target_cov[key] <= 1.0):
                raise ValueError(f"targetNextCoverage.{key} 需在 [0,1] 范围内")


# ================== 用户输入包装 ==================
def build_initial_review_feedback(source_code_loc: str, class_name: str,
                                  target_coverage: Optional[Dict[str, float]] = None,
                                  session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    将用户输入的 Java 代码、类名、目标覆盖率等信息包装成符合 2.3 规范的
    初始 ReviewFeedback 消息，用于启动第一轮迭代。
    """
    if target_coverage is None:
        target_coverage = {"lineCoverage": 0.8, "branchCoverage": 0.7, "methodCoverage": 0.75}
    # 提取简单类名（不包含包路径）用于显示，实际全限定名由输入 class_name 提供
    simple_name = class_name.split('.')[-1]
    header = build_message_header(source_code_loc,"ReviewFeedback", parent_id="0", session_id=session_id)
    feedback = {
        **header,
        "sourceClassName": class_name,
        "testClassName": f"{class_name}Test",  # 约定测试类名，出题人可覆盖
        "overallAssessment": {
            "qualityScore": 0.0,
            "coverageAdequacy": "INSUFFICIENT",
            "normativeLevel": "ACCEPTABLE",
            "summary": f"初始请求：为 {simple_name} 生成单元测试，目标覆盖率：行{target_coverage.get('lineCoverage')}，分支{target_coverage.get('branchCoverage')}，方法{target_coverage.get('methodCoverage')}"
        },
        "issueDetails": [],  # 初始无具体问题
        "iterationAdvice": {
            "shouldContinue": True,
            "focusArea": ["全方法覆盖", "边界值测试", "异常场景"],
            "targetNextCoverage": target_coverage
        }
    }
    # 验证构造的初始消息格式正确
    validate_review_feedback(feedback)
    return feedback


# ================== 主控循环 ==================
def run_test_generation(source_code_loc: str, class_name: str, class_description: str, max_iterations: int,
                        target_coverage: Optional[Dict[str, float]] = None) -> None:
    """
    串联三个模型的主控函数。
    :param source_code_loc: Java 被测类源代码地址
    :param class_name: 被测类的全限定名（如 "com.example.Calculator"）
    :param class_description: 被测类功能描述
    :param max_iterations: 最大迭代轮次
    :param target_coverage: 可选目标覆盖率，如 {"lineCoverage": 0.85, ...}
    """
    print("=== 启动多模型协作 Java 单元测试生成 ===\n")
    # 1. 构造初始评审反馈（作为出题人的第一次输入）
    current_feedback = build_initial_review_feedback(source_code_loc, class_name,
                                                     target_coverage)
    session_id = current_feedback["sessionId"]
    print(f"会话 ID: {session_id}")
    print(f"初始目标覆盖率: {current_feedback['iterationAdvice']['targetNextCoverage']}\n")

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"---------- 第 {iteration} 轮迭代 ----------")

        # ----- 步骤1：调用出题人模型 -----
        print(">> 调用出题人模型生成测试用例...")
        try:
            test_case_msg = examiner_generate(source_code_loc, class_name, class_description,
                                  iteration, current_feedback)
            # 验证出题人输出格式
            validate_generated_test_case(test_case_msg)
            print("  出题人输出格式验证通过。")
            # 确保消息头中的 sessionId 与本会话一致（若不匹配则修正，实际应由模型遵守）
            test_case_msg["sessionId"] = session_id
            test_case_msg["parentMessageId"] = current_feedback["messageId"]
        except Exception as e:
            print(f"  出题人模型出错或格式错误: {e}")
            break

        # ----- 步骤2：调用解题人模型 -----
        print(">> 调用解题人模型执行测试...")
        try:
            exec_report_msg = solver_execute(test_case_msg)
            validate_execution_report(exec_report_msg)
            print("  解题人输出格式验证通过。")
            exec_report_msg["sessionId"] = session_id
            exec_report_msg["parentMessageId"] = test_case_msg["messageId"]
        except Exception as e:
            print(f"  解题人模型出错或格式错误: {e}")
            break
        
        print(f"exec_report_msg:{exec_report_msg}")

        # ----- 步骤3：调用评审员模型 -----
        print(">> 调用评审员模型评估...")
        review_feedback_msg = None
        try:
            review_feedback_msg = reviewer_review(exec_report_msg, test_case_msg["testCodeLoc"])

            # 关键：先打印 reviewer 的原始输出，确保“feedback 可见”
            print("  [RAW] ReviewFeedback：")
            print(json.dumps(review_feedback_msg, indent=2, ensure_ascii=False))

            # 再进行格式校验（即使校验失败，你也已经看到 RAW 了）
            validate_review_feedback(review_feedback_msg)
            print("  评审员输出格式验证通过。")

            review_feedback_msg["sessionId"] = session_id
            review_feedback_msg["parentMessageId"] = exec_report_msg["messageId"]

        except Exception as e:
            print(f"  评审员模型出错或格式错误: {e}")

            # 如果 reviewer 已返回但校验失败，也把 RAW 再打印一次（防止上面没打印到）
            if review_feedback_msg is not None:
                print("  [RAW-again] ReviewFeedback：")
                print(json.dumps(review_feedback_msg, indent=2, ensure_ascii=False))

            print(traceback.format_exc())
            break

        # ----- 检查终止条件 -----
        should_continue = review_feedback_msg["iterationAdvice"]["shouldContinue"]
        quality_score = review_feedback_msg["overallAssessment"]["qualityScore"]
        coverage_adequacy = review_feedback_msg["overallAssessment"]["coverageAdequacy"]
        print(f"  质量评分: {quality_score}, 覆盖充分性: {coverage_adequacy}")
        print(f"  是否继续迭代: {should_continue}")

        if not should_continue:
            print("\n评审员判定测试质量已满足要求，终止迭代。")
            break

        # 准备下一轮：将当前评审反馈作为历史输入
        current_feedback = review_feedback_msg
        print(f"  下一轮目标覆盖率: {current_feedback['iterationAdvice'].get('targetNextCoverage', '未指定')}\n")

    if iteration >= max_iterations:
        print(f"\n达到最大迭代次数 ({max_iterations})，停止生成。")
    print("=== 测试生成流程结束 ===")


# ================== 使用示例 ==================
import argparse

def main():
    parser = argparse.ArgumentParser(description="示例程序，演示如何使用 -n 等参数")
    parser.add_argument('-n', '--name', type=str, required=False, help='-n 传类名，或 --name 传类名')
    parser.add_argument('-l', '--loc', type=str, required=False, help='-l 传文件路径，或 --loc 传文件路径')
    parser.add_argument('-d', '--desc', type=str, required=False, help='-d 传类描述，或 --desc 传类描述')
    parser.add_argument('-i', '--iterations', type=int, required=False, help='-i 传最大迭代次数，或 --iterations 传最大迭代次数')
    parser.add_argument('-t', '--target', type=int, required=False, help='-t 传目标覆盖率，或 --target 传目标覆盖率')

    args = parser.parse_args()

    if args.name:
        print(f"类名: {args.name}")
    else:
        print("请输入类名：", end="")
        input_name = input().strip()
        args.name = input_name
        print(f"类名: {args.name}")

    if args.loc:
        print(f"文件路径: {args.loc}")
    else:
        print("请输入文件路径：", end="")
        input_loc = input().strip()
        args.loc = input_loc
        print(f"文件路径: {args.loc}")

    if args.desc:
        print(f"类描述: {args.desc}")
    else:
        print("请输入类描述：", end="")
        input_desc = input().strip()
        args.desc = input_desc
        print(f"类描述: {args.desc}")

    if args.iterations is not None:
        print(f"最大迭代次数: {args.iterations}")
    else:
        print("默认迭代次数：3")
        args.iterations = 3

    if args.target is not None:
        print(f"目标覆盖率: {args.target}")
        demo_target = {"lineCoverage": args.target, "branchCoverage": args.target, "methodCoverage": args.target}
    else:
        print("默认目标覆盖率：行0.8，分支0.7，方法0.75")
        demo_target = {"lineCoverage": 0.8, "branchCoverage": 0.7, "methodCoverage": 0.75}

    run_test_generation(args.loc, args.name, args.desc, args.iterations, demo_target)

if __name__ == "__main__":
    main()