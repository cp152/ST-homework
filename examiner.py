import os
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


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


def _build_test_code(source_simple: str, test_simple: str, package_in_source: Optional[str]) -> str:
    pkg_line = f"package {package_in_source};\n\n" if package_in_source else ""
    # 这里生成的测试是“可跑通版本”，覆盖除数为0与非0
    return f"""{pkg_line}import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class {test_simple} {{

    @Test
    void main_whenSecondNonZero_printsDivisionAndModulo() {{
        String input = "8\\n2\\n";

        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;

        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();

        try {{
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            {source_simple}.main(new String[0]);
        }} finally {{
            System.setIn(originalIn);
            System.setOut(originalOut);
        }}

        String s = out.toString(StandardCharsets.UTF_8);

        assertTrue(s.contains("8 + 2 = 10"));
        assertTrue(s.contains("8 - 2 = 6"));
        assertTrue(s.contains("8 * 2 = 16"));
        assertTrue(s.contains("8 / 2 = 4"));
        assertTrue(s.contains("8 % 2 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }}

    @Test
    void main_whenSecondZero_printsZeroDivMessage() {{
        String input = "8\\n0\\n";

        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;

        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();

        try {{
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            {source_simple}.main(new String[0]);
        }} finally {{
            System.setIn(originalIn);
            System.setOut(originalOut);
        }}

        String s = out.toString(StandardCharsets.UTF_8);

        assertTrue(s.contains("8 + 0 = 8"));
        assertTrue(s.contains("8 - 0 = 8"));
        assertTrue(s.contains("8 * 0 = 0"));
        assertTrue(s.contains("除数不能为0，无法进行除法和取余运算。"));

        assertFalse(s.contains(" / 0 = "));
        assertFalse(s.contains(" % 0 = "));
    }}
}}
"""


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
    test_code_loc = os.path.join(out_dir, f"{test_simple}.java")

    test_code = _build_test_code(source_simple=source_simple,
                                 test_simple=test_simple,
                                 package_in_source=package_in_source)

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