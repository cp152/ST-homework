import os
import re
import uuid
import prompts
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import os
from openai import OpenAI

# 从环境变量读取 key，更安全
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "My Demo",
    },
)


_RE_PACKAGE = re.compile(r"^\s*package\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*;\s*$", re.MULTILINE)


def _uuid() -> str:
    return str(uuid.uuid4())


def _iso_ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _detect_package(java_source: str) -> Optional[str]:
    m = _RE_PACKAGE.search(java_source)
    return m.group(1) if m else None


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _split_fqn(class_name: str) -> Tuple[Optional[str], str]:
    """
    输入可能是 'Source1' 或 'com.example.Source1'
    返回 (package, simpleName)
    注意：最终以源码文件中的 package 为准（若源码无 package，则不输出 package）。
    """
    if not class_name or "." not in class_name:
        return None, class_name
    parts = class_name.split(".")
    return ".".join(parts[:-1]), parts[-1]


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _build_test_code(source_simple: str, package_in_source: Optional[str], class_description:str ,source_code:str,previous_feedback: str) -> str:
    try:
        prompt = prompts.get_generate_prompt(source_simple,package_in_source,class_description,source_code,previous_feedback)
        # print(f"prompt:{prompt}")

        response = client.chat.completions.create (
            model="deepseek/deepseek-v4-flash",   
            messages=[
                {"role": "user", 
                 "content": prompt}
            ]
        )
        # print(response)
        return response.choices[0].message.content

    except Exception as e:
        print(f"调用出错：{e}")


def generate(*args, **kwargs) -> Dict[str, Any]:
    """
    兼容两种调用方式：
    1) generate(class_name, class_description, iteration, previous_feedback)
    2) generate(source_code_loc, class_name, class_description, iteration, previous_feedback)
    """
    if len(args) == 4:
        class_name, class_description, iteration, previous_feedback = args
        source_code_loc = previous_feedback.get("sourceCodeLoc")
    elif len(args) == 5:
        source_code_loc, class_name, class_description, iteration, previous_feedback = args
    else:
        raise TypeError("examiner.generate 参数数量应为 4 或 5")

    # 从 previous_feedback 继承 sessionId / parentMessageId（main 后面会再覆盖，但此处必须先满足校验）
    session_id = previous_feedback.get("sessionId")
    parent_id = previous_feedback.get("messageId")

    # 目标覆盖率：优先使用上一轮 reviewer 的 targetNextCoverage
    target_cov = None
    try:
        target_cov = (previous_feedback.get("iterationAdvice") or {}).get("targetNextCoverage")
    except Exception:
        target_cov = None
    if not target_cov:
        target_cov = {"lineCoverage": 0.8, "branchCoverage": 0.7, "methodCoverage": 0.75}

    # 解析 class 名（simpleName 用于生成测试代码引用）
    _, source_simple = _split_fqn(str(class_name))
    test_simple = f"{source_simple}Test"

    # 读取源码以获取 package（以源码 package 为准）
    if not source_code_loc or not os.path.exists(source_code_loc):
        raise FileNotFoundError(f"sourceCodeLoc not found: {source_code_loc}")

    source_code = _read_text(source_code_loc)
    package_in_source = _detect_package(source_code)

    # 写出测试文件：必须实际落盘，才能通过 validate_generated_test_case 的 exists 检查
    out_dir = os.path.join(".", "generated_tests")
    _ensure_dir(out_dir)
    test_code_loc = os.path.join(out_dir, f"{test_simple}_{iteration}.java")

    test_code = _build_test_code(source_simple=source_simple,
                                 package_in_source=package_in_source,
                                 class_description = class_description,
                                 source_code = source_code,
                                 previous_feedback = previous_feedback)

    with open(test_code_loc, "w", encoding="utf-8") as f:
        f.write(test_code)

    msg = {
        "sourceCodeLoc": source_code_loc,
        "protocolVersion": "1.0",
        "messageId": _uuid(),
        "sessionId": session_id or _uuid(),
        "parentMessageId": parent_id,
        "timestamp": _iso_ts(),
        "messageType": "GeneratedTestCase",

        "sourceClassName": class_name,
        "testClassName": test_simple if not package_in_source else f"{package_in_source}.{test_simple}",
        "testCodeLoc": test_code_loc,

        "requiredEnvironment": {
            "javaVersion": "17",
            "junitVersion": "5.10.2"
        },

        "targetCoverage": target_cov
    }
    return msg