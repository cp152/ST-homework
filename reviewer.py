import os
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from openai import OpenAI


# ===================== OpenRouter client =====================
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "LLM Reviewer",
    },
)

REVIEWER_MODEL = os.getenv("REVIEWER_MODEL", "deepseek/deepseek-v4-flash")


# ===================== constants =====================
ALLOWED_CATEGORIES = {
    "COVERAGE_GAP",
    "ASSERTION",
    "EXCEPTION_HANDLING",
    "EDGE_CASE",
    "MOCK_USAGE",
    "CODE_STYLE",
    "TEST_REDUNDANCY",
}
ALLOWED_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}


# ===================== utils =====================
def _uuid() -> str:
    return str(uuid.uuid4())


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clamp01(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = float(default)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _truncate(s: str, n: int = 20000) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + f"\n...(truncated, total={len(s)} chars)"


def _read_text(path: Optional[str]) -> str:
    if not path:
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def _strip_code_fences(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def _extract_json_object(s: str) -> str:
    s = _strip_code_fences(s)
    if s.startswith("{") and s.endswith("}"):
        return s
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in model output")
    return m.group(0)


def _targets_from_report(execution_report: Dict[str, Any]) -> Dict[str, float]:
    t = execution_report.get("targetCoverage")
    if not isinstance(t, dict):
        t = {"lineCoverage": 0.9, "branchCoverage": 0.8, "methodCoverage": 0.75}
    return {
        "lineCoverage": _clamp01(t.get("lineCoverage", 0.9), 0.9),
        "branchCoverage": _clamp01(t.get("branchCoverage", 0.8), 0.8),
        "methodCoverage": _clamp01(t.get("methodCoverage", 0.75), 0.75),
    }


def _coverage_adequacy(line_cov: float) -> str:
    if line_cov < 0.5:
        return "INSUFFICIENT"
    if line_cov < 0.8:
        return "ADEQUATE"
    if line_cov < 0.9:
        return "GOOD"
    return "EXCELLENT"


def _compute_should_continue(execution_report: Dict[str, Any],
                            issues: List[Dict[str, Any]],
                            targets: Dict[str, float]) -> bool:
    cr = execution_report.get("compileResult") or {}
    compile_ok = bool(cr.get("success", False))
    status = str(execution_report.get("executionStatus") or "UNKNOWN")

    er = execution_report.get("executionResults") or {}
    failed = int(er.get("failed", 0) or 0)
    errors = int(er.get("errors", 0) or 0)

    cov = execution_report.get("coverage") or {}
    line_cov = float(cov.get("lineCoverage", 0.0) or 0.0)
    branch_cov = float(cov.get("branchCoverage", 0.0) or 0.0)
    method_cov = float(cov.get("methodCoverage", 0.0) or 0.0)

    has_high = any((it or {}).get("severity") == "HIGH" for it in (issues or []))

    if not compile_ok:
        return True
    if status != "SUCCESS":
        return True
    if failed + errors > 0:
        return True
    if has_high:
        return True
    if line_cov < targets["lineCoverage"] or branch_cov < targets["branchCoverage"] or method_cov < targets["methodCoverage"]:
        return True

    uncovered = cov.get("uncoveredItems") or []
    if any((x or {}).get("type") == "BRANCH" for x in uncovered):
        return True

    return False


def _sanitize_issue(it: Dict[str, Any]) -> Dict[str, Any]:
    it = dict(it or {})
    it["issueId"] = str(it.get("issueId") or _uuid())

    cat = str(it.get("category") or "CODE_STYLE").strip()
    if cat not in ALLOWED_CATEGORIES:
        cat = "CODE_STYLE"
    it["category"] = cat

    sev = str(it.get("severity") or "MEDIUM").strip()
    if sev not in ALLOWED_SEVERITIES:
        sev = "MEDIUM"
    it["severity"] = sev

    it["targetMethod"] = str(it.get("targetMethod") or "UNKNOWN")
    it["description"] = str(it.get("description") or "")
    it["suggestion"] = str(it.get("suggestion") or "")
    it["relatedCoverageItemId"] = it.get("relatedCoverageItemId", None)
    return it


def _sanitize_feedback(raw: Dict[str, Any], execution_report: Dict[str, Any]) -> Dict[str, Any]:
    targets = _targets_from_report(execution_report)
    cov = execution_report.get("coverage") or {}
    line_cov = _clamp01(cov.get("lineCoverage", 0.0), 0.0)
    branch_cov = _clamp01(cov.get("branchCoverage", 0.0), 0.0)
    method_cov = _clamp01(cov.get("methodCoverage", 0.0), 0.0)

    out = dict(raw or {})

    # header强制对齐会话
    out["sourceCodeLoc"] = execution_report.get("sourceCodeLoc")
    out["protocolVersion"] = execution_report.get("protocolVersion", "1.0")
    out["messageId"] = _uuid()
    out["sessionId"] = execution_report.get("sessionId") or out.get("sessionId") or _uuid()
    out["parentMessageId"] = execution_report.get("messageId") or out.get("parentMessageId")
    out["timestamp"] = _ts()
    out["messageType"] = "ReviewFeedback"
    out["sourceClassName"] = execution_report.get("sourceClassName") or out.get("sourceClassName") or "UNKNOWN"
    out["testClassName"] = execution_report.get("testClassName") or out.get("testClassName") or "UNKNOWN"

    # overallAssessment
    oa = dict(out.get("overallAssessment") or {})
    qa = _clamp01(oa.get("qualityScore", 0.0), 0.0)
    if qa == 0.0 and (line_cov > 0 or branch_cov > 0):
        # 给一个保守的回填，避免模型缺字段
        qa = round(_clamp01(0.4 * line_cov + 0.4 * branch_cov + 0.2 * 0.6, 0.0), 2)
    oa["qualityScore"] = qa
    oa["coverageAdequacy"] = str(oa.get("coverageAdequacy") or _coverage_adequacy(line_cov))
    oa["normativeLevel"] = str(oa.get("normativeLevel") or "ACCEPTABLE")
    oa["summary"] = str(oa.get("summary") or "Auto-generated review summary.")
    out["overallAssessment"] = oa

    # issueDetails
    issues = out.get("issueDetails")
    if not isinstance(issues, list):
        issues = []
    issues = [_sanitize_issue(x) for x in issues]
    out["issueDetails"] = issues

    # iterationAdvice
    ia = dict(out.get("iterationAdvice") or {})
    focus = ia.get("focusArea")
    if not isinstance(focus, list):
        focus = []
    ia["focusArea"] = [str(x) for x in focus if x is not None]

    # targetNextCoverage：不得低于 targets
    tnc = dict(ia.get("targetNextCoverage") or {})
    ia["targetNextCoverage"] = {
        "lineCoverage": max(_clamp01(tnc.get("lineCoverage", targets["lineCoverage"]), targets["lineCoverage"]), targets["lineCoverage"]),
        "branchCoverage": max(_clamp01(tnc.get("branchCoverage", targets["branchCoverage"]), targets["branchCoverage"]), targets["branchCoverage"]),
        "methodCoverage": max(_clamp01(tnc.get("methodCoverage", targets["methodCoverage"]), targets["methodCoverage"]), targets["methodCoverage"]),
    }

    # shouldContinue：按规则重算，保证一致
    ia["shouldContinue"] = bool(_compute_should_continue(execution_report, issues, targets))
    out["iterationAdvice"] = ia

    return out


# ===================== assertionEvaluation summarizer =====================
def _summarize_assertion_evaluation(execution_report: Dict[str, Any]) -> Dict[str, Any]:
    er = execution_report.get("executionResults") or {}
    ae = er.get("assertionEvaluation") or {}
    if not isinstance(ae, dict):
        return {"available": False}

    summary = ae.get("summary") or {}
    unmatched = ae.get("unmatched") or []
    matched = ae.get("matched") or []
    not_exec = ae.get("notExecuted") or []

    # 取前若干条给 LLM
    def pick(arr: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
        out = []
        for x in arr[:n]:
            out.append({
                "testMethodName": x.get("testMethodName"),
                "file": x.get("file"),
                "lineNumber": x.get("lineNumber"),
                "assertionText": _truncate(str(x.get("assertionText") or ""), 300),
                "failureType": x.get("failureType"),
                "failureMessage": _truncate(str(x.get("failureMessage") or ""), 300),
            })
        return out

    return {
        "available": True,
        "summary": {
            "matchedCount": summary.get("matchedCount", len(matched)),
            "unmatchedCount": summary.get("unmatchedCount", len(unmatched)),
            "notExecutedCount": summary.get("notExecutedCount", len(not_exec)),
        },
        "topUnmatched": pick(unmatched, 8),
        "topMatched": pick(matched, 5),
        "topNotExecuted": pick(not_exec, 5),
        "_builderError": ae.get("_error"),
    }


# ===================== prompt =====================
def _build_prompt(execution_report: Dict[str, Any], source_code: str, test_code: str) -> str:
    targets = _targets_from_report(execution_report)
    cov = execution_report.get("coverage") or {}
    env = execution_report.get("environment") or {}
    er = execution_report.get("executionResults") or {}

    ae_summary = _summarize_assertion_evaluation(execution_report)

    # 对 LLM 更友好的精简输入（避免把超长 stderr 全塞进去）
    maven_stdout = _truncate(str(er.get("_mavenStdout") or ""), 8000)
    maven_stderr = _truncate(str(er.get("_mavenStderr") or ""), 8000)

    compact = {
        "executionStatus": execution_report.get("executionStatus"),
        "compileResult": execution_report.get("compileResult"),
        "executionNumbers": {
            "total": er.get("totalMethods"),
            "passed": er.get("passed"),
            "failed": er.get("failed"),
            "errors": er.get("errors"),
            "skipped": er.get("skipped"),
        },
        "targetCoverage": targets,
        "coverage": {
            "lineCoverage": cov.get("lineCoverage"),
            "branchCoverage": cov.get("branchCoverage"),
            "methodCoverage": cov.get("methodCoverage"),
            "uncoveredItemsTop": (cov.get("uncoveredItems") or [])[:10],
        },
        "environmentHints": {
            "javaVersion": env.get("javaVersion"),
            "jacocoXml": env.get("jacocoXml"),
            "mavenVerifyExitCode": env.get("mavenVerifyExitCode"),
        },
        "assertionEvaluation": ae_summary,
        "mavenFailureStdout": maven_stdout,
        "mavenFailureStderr": maven_stderr,
    }

    schema = {
        "sourceCodeLoc": "",
        "protocolVersion": "1.0",
        "messageId": "",
        "sessionId": "",
        "parentMessageId": "",
        "timestamp": "",
        "messageType": "ReviewFeedback",
        "sourceClassName": "",
        "testClassName": "",
        "overallAssessment": {
            "qualityScore": 0.0,
            "coverageAdequacy": "",
            "normativeLevel": "",
            "summary": ""
        },
        "issueDetails": [
            {
                "issueId": "",
                "category": "",
                "severity": "",
                "targetMethod": "",
                "description": "",
                "relatedCoverageItemId": None,
                "suggestion": ""
            }
        ],
        "iterationAdvice": {
            "shouldContinue": True,
            "focusArea": [],
            "targetNextCoverage": {
                "lineCoverage": 0.0,
                "branchCoverage": 0.0,
                "methodCoverage": 0.0
            }
        }
    }

    return f"""
You are a professional Java unit test reviewer in a multi-agent framework.
You MUST output ONLY ONE valid JSON object. No Markdown. No code fences. No extra text.

Allowed issue categories ONLY:
COVERAGE_GAP, ASSERTION, EXCEPTION_HANDLING, EDGE_CASE, MOCK_USAGE, CODE_STYLE, TEST_REDUNDANCY
Allowed severity ONLY: HIGH, MEDIUM, LOW

Critical rules:
1) Use targetCoverage from input. Do NOT use hardcoded thresholds.
2) If there are failing tests, prioritize fixing WRONG ASSERTIONS / WRONG EXPECTATIONS.
   Use assertionEvaluation.topUnmatched to pinpoint the exact failing assertion lines and texts.
3) Java semantics reminders:
   - int arithmetic overflows silently (wrap-around). Expected outputs must match int semantics.
   - ArithmeticException occurs for division/mod by zero.
   - Integer.MIN_VALUE / -1 does NOT throw ArithmeticException.
4) If jacocoXml is missing or coverage is zero while tests ran, treat it as a tooling issue (JaCoCo/JDK compatibility/report generation),
   and emit a HIGH COVERAGE_GAP issue with actionable fixes (downgrade JDK to 17/21 or upgrade JaCoCo, ensure report generation).
5) targetNextCoverage MUST be >= targetCoverage (never reduce goals).

Input summary (JSON):
{json.dumps(compact, ensure_ascii=False, indent=2)}

Source code (truncated):
{_truncate(source_code, 12000)}

Test code (truncated):
{_truncate(test_code, 12000)}

Required output JSON schema (structure only, fill with real values):
{json.dumps(schema, ensure_ascii=False, indent=2)}

Return ONLY the JSON object now.
""".strip()


# ===================== fallback =====================
def _fallback_feedback(execution_report: Dict[str, Any], err: str) -> Dict[str, Any]:
    targets = _targets_from_report(execution_report)
    cov = execution_report.get("coverage") or {}
    line_cov = _clamp01(cov.get("lineCoverage", 0.0), 0.0)

    # 基于 assertionEvaluation 做最小可执行建议
    ae = _summarize_assertion_evaluation(execution_report)
    unmatched = (ae.get("topUnmatched") or []) if ae.get("available") else []

    issues = []
    if unmatched:
        issues.append({
            "issueId": _uuid(),
            "category": "ASSERTION",
            "severity": "HIGH",
            "targetMethod": unmatched[0].get("testMethodName") or "UNKNOWN",
            "description": "There are failing assertions. Use assertionEvaluation to fix exact failing assertion lines.",
            "relatedCoverageItemId": None,
            "suggestion": "Fix these failing assertions first: " + json.dumps(unmatched[:3], ensure_ascii=False)
        })
    else:
        issues.append({
            "issueId": _uuid(),
            "category": "CODE_STYLE",
            "severity": "HIGH",
            "targetMethod": "UNKNOWN",
            "description": "LLM reviewer failed; fallback feedback used.",
            "relatedCoverageItemId": None,
            "suggestion": err
        })

    out = {
        "sourceCodeLoc": execution_report.get("sourceCodeLoc"),
        "protocolVersion": execution_report.get("protocolVersion", "1.0"),
        "messageId": _uuid(),
        "sessionId": execution_report.get("sessionId") or _uuid(),
        "parentMessageId": execution_report.get("messageId") or "0",
        "timestamp": _ts(),
        "messageType": "ReviewFeedback",
        "sourceClassName": execution_report.get("sourceClassName") or "UNKNOWN",
        "testClassName": execution_report.get("testClassName") or "UNKNOWN",
        "overallAssessment": {
            "qualityScore": _clamp01(0.2, 0.2),
            "coverageAdequacy": _coverage_adequacy(line_cov),
            "normativeLevel": "ACCEPTABLE",
            "summary": f"Fallback review generated due to error: {err}"
        },
        "issueDetails": issues,
        "iterationAdvice": {
            "shouldContinue": True,
            "focusArea": ["Assertion enhancement", "Fix failing tests", "Coverage report generation"],
            "targetNextCoverage": targets
        }
    }
    return out


# ===================== public API =====================
def review(execution_report: Dict[str, Any], test_code_loc: str) -> Dict[str, Any]:
    print("========== Reviewer Agent (LLM + assertionEvaluation) ==========")

    source_code = _read_text(execution_report.get("sourceCodeLoc"))
    test_code = _read_text(test_code_loc)

    prompt = _build_prompt(execution_report, source_code, test_code)

    try:
        resp = client.chat.completions.create(
            model=REVIEWER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        raw_json = _extract_json_object(content)
        raw = json.loads(raw_json)

        out = _sanitize_feedback(raw, execution_report)
        return out

    except Exception as e:
        return _fallback_feedback(execution_report, repr(e))