```java
import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.InputMismatchException;

import static org.junit.jupiter.api.Assertions.*;

class Source1Test {

    @Test
    void main_whenSecondNonZero_printsCorrectResults() {
        String input = "15\n4\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("15 + 4 = 19"));
        assertTrue(s.contains("15 - 4 = 11"));
        assertTrue(s.contains("15 * 4 = 60"));
        assertTrue(s.contains("15 / 4 = 3"));
        assertTrue(s.contains("15 % 4 = 3"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondZero_printsDivisionErrorMessage() {
        String input = "8\n0\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("8 + 0 = 8"));
        assertTrue(s.contains("8 - 0 = 8"));
        assertTrue(s.contains("8 * 0 = 0"));
        assertTrue(s.contains("除数不能为0，无法进行除法和取余运算。"));
        assertFalse(s.contains(" / 0 = "));
        assertFalse(s.contains(" % 0 = "));
    }

    @Test
    void main_withNegativeNumbers_printsCorrectResults() {
        String input = "-10\n-3\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("-10 + -3 = -13"));
        assertTrue(s.contains("-10 - -3 = -7"));
        assertTrue(s.contains("-10 * -3 = 30"));
        assertTrue(s.contains("-10 / -3 = 3"));
        assertTrue(s.contains("-10 % -3 = -1"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_withPositiveNegative_printsCorrectResults() {
        String input = "7\n-2\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("7 + -2 = 5"));
        assertTrue(s.contains("7 - -2 = 9"));
        assertTrue(s.contains("7 * -2 = -14"));
        assertTrue(s.contains("7 / -2 = -3"));
        assertTrue(s.contains("7 % -2 = 1"));
    }

    @Test
    void main_withLargeNumbers_printsCorrectResults() {
        String input = "2147483647\n1\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("2147483647 + 1 = -2147483648"));
        assertTrue(s.contains("2147483647 - 1 = 2147483646"));
        assertTrue(s.contains("2147483647 * 1 = 2147483647"));
        assertTrue(s.contains("2147483647 / 1 = 2147483647"));
        assertTrue(s.contains("2147483647 % 1 = 0"));
    }

    @Test
    void main_withMinValueAndMinusOne_throwsArithmeticException() {
        String input = "-2147483648\n-1\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            assertThrows(ArithmeticException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("-2147483648 + -1 = 2147483647"));
        assertTrue(s.contains("-2147483648 - -1 = -2147483647"));
        assertTrue(s.contains("-2147483648 * -1 = -2147483648"));
        assertFalse(s.contains(" / "));
        assertFalse(s.contains(" % "));
    }

    @Test
    void main_withNonIntegerInput_throwsInputMismatchException() {
        String input = "abc\n2\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            assertThrows(InputMismatchException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("请输入第一个整数: "));
        assertFalse(s.contains("请输入第二个整数: "));
    }

    @Test
    void main_withFirstNonInteger_throwsInputMismatchException() {
        String input = "12.5\n3\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(in);
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            assertThrows(InputMismatchException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        String s = out.toString(StandardCharsets.UTF_8);
        assertTrue(s.contains("请输入第一个整数: "));
    }
}
```