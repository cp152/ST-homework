import os
import re
import uuid
import time
import hashlib
import platform
import tempfile
import subprocess
import shutil
from typing import Dict, Any, Optional, List, Tuple, DefaultDict
from collections import defaultdict
from xml.etree import ElementTree as ET


# =========================================================
# Basic utils
# =========================================================
def _uuid() -> str:
    return str(uuid.uuid4())


def _iso_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _truncate(s: str, max_len: int = 20000) -> str:
    if not s:
        return ""
    return s if len(s) <= max_len else (s[:max_len] + f"\n...(truncated, total={len(s)} chars)")


def _header(source_code_loc: str,
            message_type: str,
            session_id: Optional[str],
            parent_id: Optional[str],
            protocol_version: str = "1.0") -> Dict[str, Any]:
    return {
        "sourceCodeLoc": source_code_loc,
        "protocolVersion": protocol_version,
        "messageId": _uuid(),
        "sessionId": session_id or _uuid(),
        "parentMessageId": parent_id,
        "timestamp": _iso_ts(),
        "messageType": message_type,
    }


# =========================================================
# Command runner
# =========================================================
def _run_cmd(cmd: List[str], cwd: Optional[str], timeout_s: int) -> Dict[str, Any]:
    start = time.time()
    try:
        resolved = shutil.which(cmd[0])
        if resolved:
            cmd = [resolved] + cmd[1:]

        if os.name == "nt":
            low = cmd[0].lower()
            if low.endswith(".cmd") or low.endswith(".bat"):
                cmd = ["cmd.exe", "/c"] + cmd

        p = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False
        )
        return {
            "ok": True,
            "timeout": False,
            "exitCode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
            "durationMs": int((time.time() - start) * 1000),
            "cmd": cmd,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "ok": False,
            "timeout": True,
            "exitCode": None,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "durationMs": int((time.time() - start) * 1000),
            "cmd": cmd,
        }
    except Exception as e:
        return {
            "ok": False,
            "timeout": False,
            "exitCode": None,
            "stdout": "",
            "stderr": f"System error running command {cmd}: {e}",
            "durationMs": int((time.time() - start) * 1000),
            "cmd": cmd,
        }


# =========================================================
# Environment detection
# =========================================================
_RE_JAVA = re.compile(r'version\s+"([^"]+)"')
_RE_MVN = re.compile(r"Apache Maven\s+([0-9.]+)")


def _detect_java() -> Tuple[Optional[str], Optional[int], str]:
    res = _run_cmd(["java", "-version"], cwd=None, timeout_s=10)
    out = (res.get("stdout", "") + "\n" + res.get("stderr", "")).strip()
    m = _RE_JAVA.search(out)
    if not m:
        return None, None, out
    raw = m.group(1)
    major = None
    try:
        if raw.startswith("1."):
            major = int(raw.split(".")[1])
        else:
            major = int(raw.split(".")[0])
    except Exception:
        major = None
    return raw, major, out


def _detect_maven() -> Tuple[Optional[str], str]:
    res = _run_cmd(["mvn", "-v"], cwd=None, timeout_s=15)
    out = (res.get("stdout", "") + "\n" + res.get("stderr", "")).strip()
    m = _RE_MVN.search(out)
    return (m.group(1) if m else None), out


def _parse_required_java_major(v: Optional[str]) -> Optional[int]:
    if not v:
        return None
    v = str(v).strip()
    try:
        if v.startswith("1."):
            return int(v.split(".")[1])
        return int(v.split(".")[0])
    except Exception:
        return None


# =========================================================
# Source version hash (sha256)
# =========================================================
def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compute_source_hash(path: str) -> str:
    if os.path.isfile(path):
        with open(path, "rb") as f:
            digest = _sha256_bytes(f.read())
        return f"sha256:{digest}"

    if os.path.isdir(path):
        items: List[str] = []
        for root, _, names in os.walk(path):
            for n in names:
                if n.endswith(".java"):
                    items.append(os.path.join(root, n))
        items.sort()

        h = hashlib.sha256()
        base = os.path.abspath(path)
        for fp in items:
            rel = os.path.relpath(os.path.abspath(fp), base).replace("\\", "/")
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            with open(fp, "rb") as f:
                h.update(f.read())
            h.update(b"\0")
        return "sha256:" + h.hexdigest()

    return "sha256:" + _sha256_bytes(b"")


def _normalize_expected_hash(source_version: str) -> str:
    sv = (source_version or "").strip()
    if not sv:
        return ""
    if ":" not in sv:
        return "sha256:" + sv
    return sv


# =========================================================
# Java file helpers
# =========================================================
_RE_PKG = re.compile(r"^\s*package\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*;\s*$", re.MULTILINE)
_RE_PUBLIC_TYPE = re.compile(r"^\s*public\s+(?:class|interface|enum|record)\s+([A-Za-z_]\w*)\b", re.MULTILINE)
_RE_CLASS = re.compile(r"^\s*(?:public\s+)?class\s+([A-Za-z_]\w*)\b", re.MULTILINE)

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_lines(path: str) -> List[str]:
    return _read_text(path).splitlines()


def _detect_package(code: str) -> Optional[str]:
    m = _RE_PKG.search(code)
    return m.group(1) if m else None


def _detect_public_type(code: str) -> Optional[str]:
    m = _RE_PUBLIC_TYPE.search(code)
    return m.group(1) if m else None


def _detect_first_class(code: str) -> Optional[str]:
    m = _RE_CLASS.search(code)
    return m.group(1) if m else None


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _collect_java_files(path: str) -> List[str]:
    if os.path.isfile(path):
        return [path]
    files: List[str] = []
    if os.path.isdir(path):
        for root, _, names in os.walk(path):
            for n in names:
                if n.endswith(".java"):
                    files.append(os.path.join(root, n))
    return files


def _copy_java_file_into_maven(src_file: str, project_root: str, scope: str) -> str:
    """
    scope: 'main' or 'test'
    按 package 放到 src/<scope>/java/<package_path>
    若文件里有 public class X，但源文件名不是 X.java，则在沙箱中写成 X.java
    """
    code = _read_text(src_file)
    pkg = _detect_package(code)
    rel = pkg.replace(".", os.sep) if pkg else ""

    public_type = _detect_public_type(code)
    dst_name = f"{public_type}.java" if public_type else os.path.basename(src_file)

    dst_dir = os.path.join(project_root, "src", scope, "java", rel)
    _ensure_dir(dst_dir)
    dst_path = os.path.join(dst_dir, dst_name)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(code)
    return dst_path


# =========================================================
# Maven POM (JUnit5 + Mockito + JaCoCo)
# - surefire testFailureIgnore=true 让测试失败也尽量走到 verify 阶段
# =========================================================
def _pom_xml(java_release: int,
             junit_version: str,
             mockito_version: str = "5.12.0",
             jacoco_version: str = "0.8.12",
             surefire_version: str = "3.2.5") -> str:
    return f"""<project xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>llm.autotest</groupId>
  <artifactId>sandbox</artifactId>
  <version>1.0-SNAPSHOT</version>

  <properties>
    <maven.compiler.release>{java_release}</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <junit.version>{junit_version}</junit.version>
    <mockito.version>{mockito_version}</mockito.version>
  </properties>

  <dependencies>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>${{junit.version}}</version>
      <scope>test</scope>
    </dependency>

    <dependency>
      <groupId>org.mockito</groupId>
      <artifactId>mockito-core</artifactId>
      <version>${{mockito.version}}</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.mockito</groupId>
      <artifactId>mockito-junit-jupiter</artifactId>
      <version>${{mockito.version}}</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>{surefire_version}</version>
        <configuration>
          <useModulePath>false</useModulePath>
          <trimStackTrace>false</trimStackTrace>
          <testFailureIgnore>true</testFailureIgnore>
        </configuration>
      </plugin>

      <plugin>
        <groupId>org.jacoco</groupId>
        <artifactId>jacoco-maven-plugin</artifactId>
        <version>{jacoco_version}</version>
        <executions>
          <execution>
            <id>prepare-agent</id>
            <goals><goal>prepare-agent</goal></goals>
          </execution>
          <execution>
            <id>report</id>
            <phase>verify</phase>
            <goals><goal>report</goal></goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
"""


# =========================================================
# Parse Surefire reports => executionResults
# - 增加 failure/error 文本，便于断言定位
# =========================================================
def _parse_surefire_reports(surefire_dir: str) -> Dict[str, Any]:
    total = passed = failed = errors = skipped = 0
    details: List[Dict[str, Any]] = []

    if not os.path.isdir(surefire_dir):
        return {
            "totalMethods": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "details": []
        }

    for name in os.listdir(surefire_dir):
        if not (name.startswith("TEST-") and name.endswith(".xml")):
            continue
        path = os.path.join(surefire_dir, name)
        try:
            root = ET.parse(path).getroot()

            suites = []
            if root.tag == "testsuite":
                suites = [root]
            elif root.tag == "testsuites":
                suites = list(root.findall("testsuite"))
            else:
                suites = [root]

            for ts in suites:
                total += int(ts.attrib.get("tests", "0"))
                failed += int(ts.attrib.get("failures", "0"))
                errors += int(ts.attrib.get("errors", "0"))
                skipped += int(ts.attrib.get("skipped", "0"))

                for tc in ts.findall("testcase"):
                    method_name = tc.attrib.get("name", "")
                    class_name = tc.attrib.get("classname", "")
                    time_s = float(tc.attrib.get("time", "0") or 0.0)
                    duration_ms = int(time_s * 1000)

                    status = "PASSED"
                    failure_text = None
                    failure_type = None
                    failure_msg = None

                    if tc.find("skipped") is not None:
                        status = "SKIPPED"
                    else:
                        f = tc.find("failure")
                        e = tc.find("error")
                        if f is not None:
                            status = "FAILED"
                            failure_type = f.attrib.get("type")
                            failure_msg = f.attrib.get("message")
                            failure_text = (f.text or "")
                        elif e is not None:
                            status = "ERROR"
                            failure_type = e.attrib.get("type")
                            failure_msg = e.attrib.get("message")
                            failure_text = (e.text or "")

                    d = {
                        "className": class_name,
                        "methodName": method_name,
                        "status": status,
                        "durationMs": duration_ms
                    }

                    if status in ("FAILED", "ERROR"):
                        d["failureType"] = failure_type
                        d["failureMessage"] = _truncate(failure_msg or "", 2000)
                        d["failureText"] = _truncate(failure_text or "", 8000)

                    details.append(d)
        except Exception:
            continue

    passed = max(0, total - failed - errors - skipped)
    return {
        "totalMethods": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "details": details
    }


# =========================================================
# Parse JaCoCo => coverage + uncoveredItems
# =========================================================
def _parse_jacoco_coverage_and_uncovered(jacoco_xml_path: str) -> Optional[Dict[str, Any]]:
    if not os.path.isfile(jacoco_xml_path):
        return None

    root = ET.parse(jacoco_xml_path).getroot()

    counters: Dict[str, Dict[str, int]] = {}
    for c in root.findall("counter"):
        ctype = c.attrib.get("type")
        counters[ctype] = {
            "missed": int(c.attrib.get("missed", "0")),
            "covered": int(c.attrib.get("covered", "0"))
        }

    def ratio(ctype: str) -> float:
        d = counters.get(ctype, {"missed": 0, "covered": 0})
        tot = d["missed"] + d["covered"]
        return 0.0 if tot == 0 else d["covered"] / tot

    line_cov = float(ratio("LINE"))
    branch_cov = float(ratio("BRANCH"))
    method_cov = float(ratio("METHOD"))

    method_map: Dict[Tuple[str, str], List[Tuple[int, str]]] = {}
    for pkg in root.findall("package"):
        pkg_name = pkg.attrib.get("name", "")
        for cls in pkg.findall("class"):
            src_file = cls.attrib.get("sourcefilename", "")
            key = (pkg_name, src_file)
            arr = method_map.setdefault(key, [])
            for m in cls.findall("method"):
                m_name = m.attrib.get("name", "UNKNOWN")
                try:
                    m_line = int(m.attrib.get("line", "0"))
                except Exception:
                    m_line = 0
                arr.append((m_line, m_name))
            arr.sort(key=lambda x: x[0])

    def guess_method_name(pkg_slash: str, src_filename: str, line_no: int) -> str:
        key = (pkg_slash, src_filename)
        arr = method_map.get(key) or []
        candidate = "UNKNOWN"
        best = -1
        for start_line, name in arr:
            if start_line <= line_no and start_line >= best:
                best = start_line
                candidate = name
        return candidate

    uncovered_items: List[Dict[str, Any]] = []
    for pkg in root.findall("package"):
        pkg_name = pkg.attrib.get("name", "")
        for sf in pkg.findall("sourcefile"):
            src_filename = sf.attrib.get("name", "")
            for ln in sf.findall("line"):
                try:
                    nr = int(ln.attrib.get("nr", "0"))
                except Exception:
                    continue

                mi = int(ln.attrib.get("mi", "0"))
                ci = int(ln.attrib.get("ci", "0"))
                mb = int(ln.attrib.get("mb", "0"))

                if ci == 0 and mi > 0:
                    uncovered_items.append({
                        "itemId": _uuid(),
                        "type": "LINE",
                        "lineNumber": nr
                    })

                if mb > 0:
                    method_name = guess_method_name(pkg_name, src_filename, nr)
                    for i in range(mb):
                        uncovered_items.append({
                            "itemId": _uuid(),
                            "type": "BRANCH",
                            "methodName": method_name,
                            "lineNumber": nr,
                            "branchIndex": i,
                            "conditionDescription": "UNKNOWN"
                        })

    return {
        "lineCoverage": line_cov,
        "branchCoverage": branch_cov,
        "methodCoverage": method_cov,
        "uncoveredItems": uncovered_items
    }


# =========================================================
# Maven error extraction
# =========================================================
def _extract_maven_error_lines(stdout: str, stderr: str) -> List[str]:
    lines: List[str] = []
    for ln in (stdout + "\n" + stderr).splitlines():
        if "[ERROR]" in ln:
            lines.append(ln.strip())
    return lines


def _ensure_jacoco_xml(sandbox_root: str, timeout_s: int = 90) -> None:
    jacoco_xml = os.path.join(sandbox_root, "target", "site", "jacoco", "jacoco.xml")
    jacoco_exec = os.path.join(sandbox_root, "target", "jacoco.exec")

    if os.path.isfile(jacoco_xml):
        return
    if not os.path.isfile(jacoco_exec):
        return

    _run_cmd(["mvn", "-q", "-DskipTests=true", "jacoco:report"], cwd=sandbox_root, timeout_s=timeout_s)


# =========================================================
# Assertion extraction + match grouping
# =========================================================
_RE_ASSERT_CALL = re.compile(r"\bassert(?:True|False|Equals|NotEquals|Null|NotNull|Same|NotSame|ArrayEquals|IterableEquals|Throws|DoesNotThrow)\s*\(")
_RE_ASSERTIONS_DOT = re.compile(r"\bAssertions\.\s*assert")
_RE_TEST_ANNOT = re.compile(r"@Test\b")
_RE_METHOD_SIG = re.compile(r"\bvoid\s+([A-Za-z_]\w*)\s*\(")
_RE_FAIL_FRAME_METHOD = re.compile(r"\bat\s+.*\.(\w+)\(([^:()]+\.java):(\d+)\)")
_RE_FAIL_FRAME_ANY = re.compile(r"\(([^:()]+\.java):(\d+)\)")


def _extract_assertions_by_class_and_method(java_path: str) -> Tuple[Optional[str], Dict[str, List[Dict[str, Any]]]]:
    """
    解析一个测试 Java 文件，返回：
      (classSimpleName, { testMethodName: [ {lineNumber, text}, ... ] })
    行号为 1-based，与堆栈中的 Source1Test_2.java:147 对齐。
    """
    code = _read_text(java_path)
    cls = _detect_first_class(code)  # 可能 None
    lines = code.splitlines()

    by_method: Dict[str, List[Dict[str, Any]]] = {}
    pending_test = False
    last_test_line = -1000

    i = 0
    while i < len(lines):
        line = lines[i]
        if _RE_TEST_ANNOT.search(line):
            pending_test = True
            last_test_line = i
            i += 1
            continue

        # 限制：@Test 后太远还没遇到方法签名则取消
        if pending_test and i - last_test_line > 30:
            pending_test = False

        if pending_test:
            m = _RE_METHOD_SIG.search(line)
            if m:
                method = m.group(1)
                start = i
                brace = line.count("{") - line.count("}")
                j = i + 1
                while j < len(lines) and brace > 0:
                    brace += lines[j].count("{") - lines[j].count("}")
                    j += 1
                end = j  # exclusive

                asserts: List[Dict[str, Any]] = []
                for ln_idx in range(start, end):
                    ln = lines[ln_idx]
                    if _RE_ASSERT_CALL.search(ln) or _RE_ASSERTIONS_DOT.search(ln):
                        asserts.append({
                            "lineNumber": ln_idx + 1,
                            "text": ln.strip()
                        })
                by_method[method] = asserts

                pending_test = False
                i = end
                continue

        i += 1

    return cls, by_method


def _build_assertion_evaluation(execution_results: Dict[str, Any], test_code_loc: str) -> Dict[str, Any]:
    """
    根据 surefire details + 源码，构建断言匹配分组：
      matched/unmatched/notExecuted
    """
    details = execution_results.get("details") or []
    test_files = _collect_java_files(test_code_loc)

    # 1) 解析测试源码：class -> method -> assertions
    class_map: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    file_map: Dict[str, str] = {}  # basename -> path
    for fp in test_files:
        file_map[os.path.basename(fp)] = fp
        cls, by_method = _extract_assertions_by_class_and_method(fp)
        if cls:
            class_map[cls] = by_method

    def find_assertions(class_name: str, method_name: str) -> List[Dict[str, Any]]:
        simple = (class_name or "").split(".")[-1]
        if simple in class_map and method_name in class_map[simple]:
            return class_map[simple][method_name]
        # fallback：在所有类里找同名 method（避免 className 缺失）
        for _, mm in class_map.items():
            if method_name in mm:
                return mm[method_name]
        return []

    # 2) 提取失败行号
    matched: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    not_executed: List[Dict[str, Any]] = []

    for tc in details:
        method = tc.get("methodName", "")
        cls = tc.get("className", "")
        status = tc.get("status", "")
        asserts = find_assertions(cls, method)

        # 没有检测到断言也给提示（对 reviewer 有价值）
        if not asserts:
            continue

        if status == "PASSED":
            for a in asserts:
                matched.append({
                    "itemId": _uuid(),
                    "testClassName": cls,
                    "testMethodName": method,
                    "file": None,
                    "lineNumber": a["lineNumber"],
                    "assertionText": a["text"]
                })
            continue

        if status in ("FAILED", "ERROR"):
            failure_text = tc.get("failureText", "") or ""
            failure_msg = tc.get("failureMessage", "") or ""
            failure_type = tc.get("failureType", "") or ""

            # 优先找包含 method 的 frame：...method(File.java:123)
            fail_file = None
            fail_line = None

            for m in _RE_FAIL_FRAME_METHOD.finditer(failure_text):
                m_method, f, ln = m.group(1), m.group(2), m.group(3)
                if m_method == method:
                    fail_file = f
                    try:
                        fail_line = int(ln)
                    except Exception:
                        fail_line = None
                    break

            # fallback：任意 (File.java:123)
            if fail_line is None:
                m2 = _RE_FAIL_FRAME_ANY.search(failure_text)
                if m2:
                    fail_file = m2.group(1)
                    try:
                        fail_line = int(m2.group(2))
                    except Exception:
                        fail_line = None

            # 找到“最可能失败的断言”：行号==fail_line，否则找 fail_line 之前最近的 assert
            fail_assert = None
            if fail_line is not None:
                exact = [a for a in asserts if a["lineNumber"] == fail_line]
                if exact:
                    fail_assert = exact[0]
                else:
                    before = [a for a in asserts if a["lineNumber"] <= fail_line]
                    if before:
                        fail_assert = max(before, key=lambda x: x["lineNumber"])

            # 分组：失败前 matched，失败断言 unmatched，失败后 notExecuted（保守）
            if fail_assert and fail_line is not None:
                for a in asserts:
                    if a["lineNumber"] < fail_assert["lineNumber"]:
                        matched.append({
                            "itemId": _uuid(),
                            "testClassName": cls,
                            "testMethodName": method,
                            "file": fail_file,
                            "lineNumber": a["lineNumber"],
                            "assertionText": a["text"]
                        })
                    elif a["lineNumber"] == fail_assert["lineNumber"]:
                        unmatched.append({
                            "itemId": _uuid(),
                            "testClassName": cls,
                            "testMethodName": method,
                            "file": fail_file,
                            "lineNumber": a["lineNumber"],
                            "assertionText": a["text"],
                            "failureType": failure_type,
                            "failureMessage": failure_msg,
                            "failureTextSnippet": _truncate(failure_text, 1200)
                        })
                    else:
                        not_executed.append({
                            "itemId": _uuid(),
                            "testClassName": cls,
                            "testMethodName": method,
                            "file": fail_file,
                            "lineNumber": a["lineNumber"],
                            "assertionText": a["text"]
                        })
            else:
                # 定位不到行号：该方法内断言全部归为 unmatched，并带上失败信息
                for a in asserts:
                    unmatched.append({
                        "itemId": _uuid(),
                        "testClassName": cls,
                        "testMethodName": method,
                        "file": fail_file,
                        "lineNumber": a["lineNumber"],
                        "assertionText": a["text"],
                        "failureType": failure_type,
                        "failureMessage": failure_msg,
                        "failureTextSnippet": _truncate(failure_text, 1200)
                    })

    # 控制体积
    def cap(arr: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
        return arr if len(arr) <= n else arr[:n] + [{
            "itemId": _uuid(),
            "note": f"truncated: total={len(arr)}"
        }]

    return {
        "matched": cap(matched, 200),
        "unmatched": cap(unmatched, 200),
        "notExecuted": cap(not_executed, 200),
        "summary": {
            "matchedCount": len(matched),
            "unmatchedCount": len(unmatched),
            "notExecutedCount": len(not_executed),
        }
    }


# =========================================================
# Public API: execute()
# =========================================================
def execute(test_case_msg: Dict[str, Any]) -> Dict[str, Any]:
    source_code_loc = test_case_msg.get("sourceCodeLoc")
    test_code_loc = test_case_msg.get("testCodeLoc")
    source_class_name = test_case_msg.get("sourceClassName")
    test_class_name = test_case_msg.get("testClassName")
    source_version = test_case_msg.get("sourceVersion")

    required_env = test_case_msg.get("requiredEnvironment") or {}
    required_java_major = _parse_required_java_major(required_env.get("javaVersion"))
    required_junit_version = str(required_env.get("junitVersion") or "5.10.2").strip()

    session_id = test_case_msg.get("sessionId")
    parent_id = test_case_msg.get("messageId")
    protocol_version = test_case_msg.get("protocolVersion", "1.0")

    report: Dict[str, Any] = {
        **_header(source_code_loc, "ExecutionReport", session_id, parent_id, protocol_version),
        "sourceClassName": source_class_name,
        "testClassName": test_class_name,

        "executionStatus": "SYSTEM_ERROR",

        "environmentCompatibility": {
            "isCompatible": False,
            "mismatches": []
        },

        "compileResult": {
            "success": False,
            "errors": []
        },

        "executionResults": None,
        "coverage": None,

        "environment": {
            "javaVersion": None,
            "junitVersion": required_junit_version,
            "mockFramework": "Mockito 5.12.0",
            "os": platform.platform()
        }
    }

    # 0) path check
    if not source_code_loc or not os.path.exists(source_code_loc):
        report["compileResult"]["errors"] = [f"sourceCodeLoc not found: {source_code_loc}"]
        report["executionStatus"] = "SYSTEM_ERROR"
        return report

    if not test_code_loc or not os.path.exists(test_code_loc):
        report["compileResult"]["errors"] = [f"testCodeLoc not found: {test_code_loc}"]
        report["executionStatus"] = "SYSTEM_ERROR"
        return report

    # 1) sourceVersion check
    if source_version:
        expected = _normalize_expected_hash(str(source_version))
        actual = _compute_source_hash(source_code_loc)
        report["environment"]["sourceVersionExpected"] = expected
        report["environment"]["sourceVersionActual"] = actual
        if expected and expected != actual:
            report["compileResult"]["errors"] = [f"sourceVersion mismatch: expected={expected}, actual={actual}"]
            report["executionStatus"] = "SYSTEM_ERROR"
            return report

    # 2) environment compatibility
    java_raw, java_major, java_out = _detect_java()
    mvn_ver, mvn_out = _detect_maven()

    report["environment"]["javaVersion"] = str(java_major) if java_major is not None else (java_raw or "")
    report["environment"]["javaVersionRaw"] = java_raw
    report["environment"]["mavenVersion"] = mvn_ver
    report["environment"]["javaDetectOutput"] = _truncate(java_out, 4000)
    report["environment"]["mavenDetectOutput"] = _truncate(mvn_out, 4000)

    mismatches: List[Dict[str, Any]] = []
    if java_major is None:
        mismatches.append({"item": "java", "expected": required_env.get("javaVersion"), "actual": None, "message": "Cannot detect java version"})
    if mvn_ver is None:
        mismatches.append({"item": "maven", "expected": "installed", "actual": None, "message": "Cannot detect maven"})
    if required_java_major is not None and java_major is not None and java_major < required_java_major:
        mismatches.append({"item": "javaVersion", "expected": f">={required_java_major}", "actual": java_major, "message": "Java version is lower than required"})

    is_compat = (len(mismatches) == 0)
    report["environmentCompatibility"]["isCompatible"] = is_compat
    report["environmentCompatibility"]["mismatches"] = mismatches

    if not is_compat:
        report["executionStatus"] = "ENVIRONMENT_MISMATCH"
        return report

    # 3) sandbox
    sandbox_root = tempfile.mkdtemp(prefix="java-ut-sandbox-")
    try:
        with open(os.path.join(sandbox_root, "pom.xml"), "w", encoding="utf-8") as f:
            f.write(_pom_xml(
                java_release=required_java_major or java_major or 17,
                junit_version=required_junit_version,
                mockito_version="5.12.0",
            ))

        source_files = _collect_java_files(source_code_loc)
        test_files = _collect_java_files(test_code_loc)
        if not source_files:
            report["compileResult"]["errors"] = [f"No .java files found in sourceCodeLoc: {source_code_loc}"]
            report["executionStatus"] = "SYSTEM_ERROR"
            return report
        if not test_files:
            report["compileResult"]["errors"] = [f"No .java files found in testCodeLoc: {test_code_loc}"]
            report["executionStatus"] = "SYSTEM_ERROR"
            return report

        for sf in source_files:
            _copy_java_file_into_maven(sf, sandbox_root, "main")
        for tf in test_files:
            _copy_java_file_into_maven(tf, sandbox_root, "test")

        # 4) compile
        compile_res = _run_cmd(["mvn", "-q", "-DskipTests=true", "test-compile"], cwd=sandbox_root, timeout_s=120)
        if not compile_res.get("ok"):
            report["executionStatus"] = "TIMEOUT" if compile_res.get("timeout") else "SYSTEM_ERROR"
            report["compileResult"]["errors"] = _extract_maven_error_lines(compile_res.get("stdout", ""), compile_res.get("stderr", "")) \
                                            or [compile_res.get("stderr", "compile command failed")]
            return report

        if compile_res.get("exitCode") != 0:
            report["compileResult"]["success"] = False
            report["compileResult"]["errors"] = _extract_maven_error_lines(compile_res.get("stdout", ""), compile_res.get("stderr", "")) \
                                            or ["Compilation failed (no [ERROR] lines captured)."]
            report["executionStatus"] = "COMPILATION_ERROR"
            return report

        report["compileResult"]["success"] = True
        report["compileResult"]["errors"] = []

        # 5) run tests + jacoco
        # 修复点：使用正确参数 maven.test.failure.ignore=true
        test_res = _run_cmd(
            ["mvn", "-q", "-Dmaven.test.failure.ignore=true", "verify"],
            cwd=sandbox_root,
            timeout_s=180
        )
        report["environment"]["mavenVerifyExitCode"] = test_res.get("exitCode")
        report["environment"]["mavenVerifyDurationMs"] = test_res.get("durationMs")

        if not test_res.get("ok"):
            report["executionStatus"] = "TIMEOUT" if test_res.get("timeout") else "SYSTEM_ERROR"
            report["compileResult"]["errors"] = _extract_maven_error_lines(test_res.get("stdout", ""), test_res.get("stderr", "")) \
                                            or [test_res.get("stderr", "verify command failed")]
            report["executionResults"] = None
            report["coverage"] = None
            return report

        # 6) parse surefire
        surefire_dir = os.path.join(sandbox_root, "target", "surefire-reports")
        exec_stats = _parse_surefire_reports(surefire_dir)

        exec_stats["_mavenStdout"] = _truncate(test_res.get("stdout", ""), 20000)
        exec_stats["_mavenStderr"] = _truncate(test_res.get("stderr", ""), 20000)

        # 6.1) NEW: assertion evaluation grouping
        try:
            exec_stats["assertionEvaluation"] = _build_assertion_evaluation(exec_stats, test_code_loc)
        except Exception as e:
            # 不影响主流程：给 reviewer 一个提示
            exec_stats["assertionEvaluation"] = {
                "matched": [],
                "unmatched": [],
                "notExecuted": [],
                "summary": {"matchedCount": 0, "unmatchedCount": 0, "notExecutedCount": 0},
                "_error": f"assertionEvaluation build failed: {repr(e)}"
            }

        report["executionResults"] = exec_stats

        # 7) jacoco report ensure + parse
        _ensure_jacoco_xml(sandbox_root)

        jacoco_xml = os.path.join(sandbox_root, "target", "site", "jacoco", "jacoco.xml")
        cov = _parse_jacoco_coverage_and_uncovered(jacoco_xml)
        if cov is None:
            cov = {
                "lineCoverage": 0.0,
                "branchCoverage": 0.0,
                "methodCoverage": 0.0,
                "uncoveredItems": []
            }
        report["coverage"] = cov

        # 8) decide executionStatus
        failed = int(exec_stats.get("failed", 0))
        errs = int(exec_stats.get("errors", 0))

        if failed > 0:
            report["executionStatus"] = "TEST_FAILURE"
        elif errs > 0:
            report["executionStatus"] = "TEST_ERROR"
        else:
            report["executionStatus"] = "SUCCESS"

        report["environment"]["sandboxRoot"] = sandbox_root
        report["environment"]["jacocoXml"] = jacoco_xml if os.path.isfile(jacoco_xml) else None
        report["environment"]["surefireReports"] = surefire_dir if os.path.isdir(surefire_dir) else None

        return report

    except Exception as e:
        report["executionStatus"] = "SYSTEM_ERROR"
        report["compileResult"]["errors"] = [f"SYSTEM_ERROR: {e}"]
        report["executionResults"] = None
        report["coverage"] = None
        return report

    # 如需清理可启用：
    # finally:
    #     shutil.rmtree(sandbox_root, ignore_errors=True)