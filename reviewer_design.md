# Reviewer Agent Design

## 1. Overview

The Reviewer Agent is responsible for evaluating the quality of generated Java unit tests.

Its main objectives are:

- Analyze test execution results
- Evaluate test coverage
- Detect missing test scenarios
- Assess assertion quality and code规范
- Generate optimization suggestions
- Decide whether iterative refinement should continue

The Reviewer Agent serves as the core feedback component in the multi-agent collaborative testing framework.

---

# 2. Reviewer Workflow

The Reviewer Agent receives an `ExecutionReport` message from the Solver Agent and produces a `ReviewFeedback` message for the Examiner Agent.

The workflow is shown below:

```text
ExecutionReport
    ↓
Coverage Analysis
    ↓
Test Quality Analysis
    ↓
Issue Classification
    ↓
Iteration Decision
    ↓
ReviewFeedback
```

---

# 3. Input Information

The Reviewer Agent uses the following information:

| Input Source | Content |
|---|---|
| ExecutionReport.compileResult | Compilation status and errors |
| ExecutionReport.executionResults | Test pass/fail information |
| ExecutionReport.coverage | Coverage metrics and uncovered branches |
| Test Code | Generated JUnit test code |
| Source Code | Original Java source code |

---

# 4. Evaluation Dimensions

The Reviewer Agent evaluates generated tests from multiple dimensions.

---

## 4.1 Coverage Evaluation

Coverage metrics are directly obtained from JaCoCo reports.

### Evaluated Metrics

| Metric | Description |
|---|---|
| lineCoverage | Line coverage ratio |
| branchCoverage | Branch coverage ratio |
| methodCoverage | Method coverage ratio |

### Coverage Adequacy Rules

| Condition | Result |
|---|---|
| lineCoverage < 0.5 | INSUFFICIENT |
| 0.5 ≤ lineCoverage < 0.8 | ADEQUATE |
| lineCoverage ≥ 0.8 | GOOD |

Branch coverage is treated as a higher-priority metric because it better reflects path diversity.

---

## 4.2 Assertion Quality Evaluation

The Reviewer Agent evaluates whether generated tests contain meaningful assertions.

### Evaluation Criteria

- Presence of assertions
- Assertion readability
- Presence of assertion messages
- Correct expected values
- Exception assertion usage

### Typical Problems

- Missing assertions
- Weak assertions
- Incorrect expected results
- Missing `assertThrows`

---

## 4.3 Edge Case Evaluation

The Reviewer Agent analyzes whether important edge cases are covered.

### Typical Edge Cases

| Type | Example |
|---|---|
| Null Input | `null` parameters |
| Boundary Value | `Integer.MAX_VALUE` |
| Empty Input | empty string/list |
| Exception Path | invalid arguments |
| Negative Number | negative values |
| Overflow | arithmetic overflow |

---

## 4.4 Code Style Evaluation

The Reviewer Agent evaluates test readability and规范性.

### Evaluation Criteria

- Test method naming
- Use of Given-When-Then style
- Proper test isolation
- Readability
- Mockito usage规范

---

# 5. Issue Classification

Detected problems are classified into structured categories.

## Supported Categories

| Category | Description |
|---|---|
| COVERAGE_GAP | Coverage insufficient |
| ASSERTION | Assertion-related issue |
| EXCEPTION_HANDLING | Missing exception tests |
| EDGE_CASE | Missing edge-case tests |
| MOCK_USAGE | Mockito misuse |
| CODE_STYLE | Naming or readability issue |
| TEST_REDUNDANCY | Duplicate or meaningless tests |

---

# 6. Severity Levels

Each issue is assigned a severity level.

| Severity | Description |
|---|---|
| HIGH | Significantly affects test quality |
| MEDIUM | Recommended to fix |
| LOW | Minor optimization suggestion |

---

# 7. Quality Score Calculation

The Reviewer Agent calculates an overall quality score.

## Formula

```text
qualityScore =
0.4 × lineCoverage +
0.4 × branchCoverage +
0.2 × assertionQuality
```

Where:

- `assertionQuality` is estimated by the Reviewer Agent according to assertion completeness and readability.

The final score is normalized to the range [0,1].

---

# 8. Iteration Decision Strategy

The Reviewer Agent determines whether another optimization round is required.

---

## Continue Iteration Conditions

Iterative refinement continues if any of the following conditions are satisfied:

1. Line coverage is below target
2. Branch coverage is below target
3. Compilation errors exist
4. Test failures exist
5. HIGH severity issues exist

---

## Termination Conditions

The iteration process terminates when:

- Coverage targets are satisfied
- No HIGH severity issues remain
- Tests compile successfully
- Most tests pass successfully

---

# 9. Focus Area Generation

The Reviewer Agent generates optimization focus areas for the next iteration.

## Examples

| Problem | Focus Area |
|---|---|
| Low branch coverage | Branch path testing |
| Missing exceptions | Exception handling |
| Weak assertions | Assertion enhancement |
| Missing edge cases | Boundary value testing |

These focus areas are passed to the Examiner Agent to guide the next generation round.

---

# 10. Structured Output Requirement

The Reviewer Agent must always output structured JSON messages.

Natural language explanations outside JSON are not allowed.

This design ensures:

- Stable multi-agent communication
- Automatic parsing
- Experimental reproducibility
- Easier iterative optimization

---

# 11. Design Rationale

The Reviewer Agent combines:

- Rule-based evaluation
- LLM-based semantic analysis

Rule-based logic is used for:
- Coverage threshold checking
- Iteration control
- Basic scoring

LLM-based analysis is used for:
- Natural language summaries
- Suggestion generation
- Assertion quality evaluation
- Code style analysis

This hybrid strategy improves:
- Stability
- Interpretability
- Reproducibility

while preserving the flexibility of large language models.

---

# 12. Limitations

Current limitations include:

- Limited semantic understanding of complex business logic
- Dependence on LLM output stability
- Lack of mutation testing support
- Limited static analysis capability

Future work may integrate:
- Mutation testing
- AST analysis
- Symbolic execution
- More advanced quality metrics
