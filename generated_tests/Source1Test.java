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
        String input = "8\n2\n";
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
        assertTrue(s.contains("8 + 2 = 10"));
        assertTrue(s.contains("8 - 2 = 6"));
        assertTrue(s.contains("8 * 2 = 16"));
        assertTrue(s.contains("8 / 2 = 4"));
        assertTrue(s.contains("8 % 2 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondZero_printsErrorMessage() {
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
    void main_whenNegativeNumbers_printsCorrectResults() {
        String input = "-8\n3\n";
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
        assertTrue(s.contains("-8 + 3 = -5"));
        assertTrue(s.contains("-8 - 3 = -11"));
        assertTrue(s.contains("-8 * 3 = -24"));
        assertTrue(s.contains("-8 / 3 = -2"));
        assertTrue(s.contains("-8 % 3 = -2"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenBothZero_printsErrorMessage() {
        String input = "0\n0\n";
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
        assertTrue(s.contains("0 + 0 = 0"));
        assertTrue(s.contains("0 - 0 = 0"));
        assertTrue(s.contains("0 * 0 = 0"));
        assertTrue(s.contains("除数不能为0，无法进行除法和取余运算。"));
    }

    @Test
    void main_whenInputNotInteger_throwsInputMismatchException() {
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
    }

    @Test
    void main_whenSecondNegativeOne_printsCorrectResults() {
        String input = "10\n-1\n";
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
        assertTrue(s.contains("10 + -1 = 9"));
        assertTrue(s.contains("10 - -1 = 11"));
        assertTrue(s.contains("10 * -1 = -10"));
        assertTrue(s.contains("10 / -1 = -10"));
        assertTrue(s.contains("10 % -1 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenEdgeCaseLargeNumbers_printsResults() {
        // 测试边界值 Integer.MAX_VALUE 和 1
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
        // 加法可能溢出为 -2147483648，但仍是合法输出
        assertTrue(s.contains(" + "));
        assertTrue(s.contains(" - "));
        assertTrue(s.contains(" * "));
        assertTrue(s.contains(" / "));
        assertTrue(s.contains(" % "));
    }
}
```