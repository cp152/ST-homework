from typing import Dict, Any, Optional, Tuple
def get_generate_prompt(source_simple: str, package_in_source: Optional[str], class_description:str ,source_code:str,privious_feedback: str) -> str:
    return f"""
你是一个资深 Java 测试开发工程师，请基于以下信息为指定的 Java 类编写高质量的 JUnit 5 单元测试。

你将收到 5 个输入参数：
- source_simple：待测类的类名（不含包名）
- package_in_source：待测类所在文件的包声明（可能为 None 或完整 package 语句，如 "package com.example; "）
- class_description：对待测类功能的自然语言描述，包含主要职责、关键分支和边界条件
- source_code：待测类的完整源代码
- privious_feedback：上一轮单元测试的反馈意见，说明上一次测试存在的问题或需要改进、特别注意的地方。如果该字段为“无”或空，表示没有历史反馈，请按最佳实践自由设计。

你的任务：
生成一个完整的 JUnit 5 测试类，满足以下要求：
1. 测试类命名为 `{{source_simple}}Test`。
2. 如果 `package_in_source` 不为 None 且非空，则将测试类放在相同包中（即在文件开头添加对应的 package 声明）；否则省略 package 声明。
3. 所有测试方法使用 `@Test` 注解，并遵循命名规范：`methodName_condition_expectedBehavior`。
4. 根据 `class_description` 和 `source_code` 覆盖所有关键逻辑路径，包括正常情况、边界条件、异常路径和重要分支。特别关注：
   - 公共实例方法 / 静态方法的返回值
   - 通过标准输入/输出交互的方法（需正确重定向 System.in / System.out 并恢复）
   - 异常抛出（使用 `assertThrows`）
   - 状态变更、副作用验证
5. 测试应当相互独立，不依赖执行顺序。
6. **必须认真考虑 `privious_feedback` 中的每一条意见**，修正之前的问题，并在测试设计或注释中体现出针对性的改进。
7. 代码中需包含必要的 import 语句，使用 JUnit 5（org.junit.jupiter.api）和标准库。如果涉及模拟，优先使用 Mockito（org.mockito），并在代码中正确初始化和注入。
8. 仅输出测试类代码，不要包含额外解释。

输出格式模板：
```java
import org.junit.jupiter.api.Test;
// ... 其他导入 ...

class Test{{source_simple}} {{
    // 测试方法...
    @Test
    void methodName_condition_expectedBehavior() {{
        // ...
    }}
    // ...
}}
```

下面是一个包含标准输入输出测试的示例，请参照其结构和风格：

【示例输入】
source_simple：Source1
package_in_source：None
class_description：命令行交互式计算器：加减乘除与取余，含除数为0分支
source_code：
import java.util.Scanner;
public class Source1 {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        System.out.print("请输入第一个整数: ");
        int num1 = scanner.nextInt();
        System.out.print("请输入第二个整数: ");
        int num2 = scanner.nextInt();
        System.out.println("\\n运算结果如下：");
        System.out.println(num1 + " + " + num2 + " = " + (num1 + num2));
        System.out.println(num1 + " - " + num2 + " = " + (num1 - num2));
        System.out.println(num1 + " * " + num2 + " = " + (num1 * num2));
        if (num2 != 0) {{
            System.out.println(num1 + " / " + num2 + " = " + (num1 / num2));
            System.out.println(num1 + " % " + num2 + " = " + (num1 % num2));
        }} else {{
            System.out.println("除数不能为0，无法进行除法和取余运算。");
        }}
        scanner.close();
    }}
}}
privious_feedback：无

【示例输出】
import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class TestSource1 {{

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
            Source1.main(new String[0]);
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
            Source1.main(new String[0]);
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

现在，请根据以下输入生成测试代码（注意 privious_feedback 中的反馈，务必在测试中落实）：

source_simple：{source_simple}
package_in_source：{package_in_source}
class_description：{class_description}
source_code：{source_code}
privious_feedback：{privious_feedback}

请保证你的输出是一个Java代码，不包含除了代码内容以外的信息。
"""