```java
import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class TestSource1 {

    @Test
    void main_whenBothPositive_printsCorrectResults() {
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
    void main_whenSecondZero_printsZeroDivMessage() {
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
    void main_whenBothNegative_printsCorrectResults() {
        String input = "-8\n-2\n";
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
        assertTrue(s.contains("-8 + -2 = -10"));
        assertTrue(s.contains("-8 - -2 = -6"));
        assertTrue(s.contains("-8 * -2 = 16"));
        assertTrue(s.contains("-8 / -2 = 4"));
        assertTrue(s.contains("-8 % -2 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenPositiveDividedByNegative_printsCorrectResults() {
        String input = "15\n-4\n";
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
        assertTrue(s.contains("15 + -4 = 11"));
        assertTrue(s.contains("15 - -4 = 19"));
        assertTrue(s.contains("15 * -4 = -60"));
        assertTrue(s.contains("15 / -4 = -3"));
        assertTrue(s.contains("15 % -4 = 3"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenDividendZeroAndDivisorNonZero_printsCorrectResults() {
        String input = "0\n5\n";
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
        assertTrue(s.contains("0 + 5 = 5"));
        assertTrue(s.contains("0 - 5 = -5"));
        assertTrue(s.contains("0 * 5 = 0"));
        assertTrue(s.contains("0 / 5 = 0"));
        assertTrue(s.contains("0 % 5 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenBoundaryValues_printsCorrectResults() {
        // Use Integer.MAX_VALUE and Integer.MIN_VALUE to test edge cases
        String max = String.valueOf(Integer.MAX_VALUE);
        String min = String.valueOf(Integer.MIN_VALUE);
        String input = max + "\n" + min + "\n";
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
        // These calculations are standard Java arithmetic
        assertTrue(s.contains("2147483647 + -2147483648 = -1"));
        assertTrue(s.contains("2147483647 - -2147483648 = -1"));
        assertTrue(s.contains("2147483647 * -2147483648 = -2147483648"));
        assertTrue(s.contains("2147483647 / -2147483648 = 0"));
        assertTrue(s.contains("2147483647 % -2147483648 = 2147483647"));
        assertFalse(s.contains("除数不能为0"));
    }
}
```