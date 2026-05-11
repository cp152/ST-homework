import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class Source1Test {

    @Test
    void main_whenSecondNonZero_printsCorrectArithmeticResultsForPositiveNumbers() {
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
    void main_whenSecondNonZeroWithNegativeNumbers_printsCorrectResults() {
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
    void main_whenSecondZero_printsZeroDivMessageAndNoDivisionOrModulo() {
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
    void main_whenFirstIsZero_printsCorrectResults() {
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
    void main_whenNumbersAreEqual_printsCorrectSelfArithmetic() {
        String input = "7\n7\n";

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

        assertTrue(s.contains("7 + 7 = 14"));
        assertTrue(s.contains("7 - 7 = 0"));
        assertTrue(s.contains("7 * 7 = 49"));
        assertTrue(s.contains("7 / 7 = 1"));
        assertTrue(s.contains("7 % 7 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondIsNegative_printsCorrectResults() {
        String input = "10\n-3\n";

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

        assertTrue(s.contains("10 + -3 = 7"));
        assertTrue(s.contains("10 - -3 = 13"));
        assertTrue(s.contains("10 * -3 = -30"));
        assertTrue(s.contains("10 / -3 = -3"));
        assertTrue(s.contains("10 % -3 = 1"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenBothZero_printsCorrectMessageForDivisionByZero() {
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

        assertFalse(s.contains(" / 0 = "));
        assertFalse(s.contains(" % 0 = "));
    }

    @Test
    void main_whenInputIsLargeIntegers_boundaryTest() {
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
        assertFalse(s.contains("除数不能为0"));
    }
}