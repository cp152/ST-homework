def get_review_prompt(
        source_code,
        test_code,
        execution_report,
        previous_feedback=None
):
    return f"""

你是一名高级Java测试专家。

你的任务不是生成测试，
而是评审一个JUnit测试质量。


被测代码:

{source_code}


测试代码:

{test_code}


测试执行结果:

{execution_report}


历史反馈:

{previous_feedback}


请分析：

1. 测试是否覆盖主要逻辑路径
2. 是否存在遗漏的边界情况
3. 是否存在无效断言
4. 是否需要增加异常测试
5. 下一轮测试生成应该关注什么


严格输出JSON:

{{
 "qualityScore":0-1,
 "coverageAdequacy":"",
 "normativeLevel":"",
 "summary":"",

 "issues":[
    {{
      "type":"",
      "description":"",
      "suggestion":""
    }}
 ],

 "nextFocus":[
    ""
 ],

 "shouldContinue":true/false
}}

不要输出任何解释。
"""