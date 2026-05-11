import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class Source1Test {

    @Test
    void main_whenSecondNonZero_printsAllResultsIncludingDivisionAndModulo() {
        String input = "10\n3\n";
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("10 + 3 = 13"));
        assertTrue(output.contains("10 - 3 = 7"));
        assertTrue(output.contains("10 * 3 = 30"));
        assertTrue(output.contains("10 / 3 = 3"));
        assertTrue(output.contains("10 % 3 = 1"));
        assertFalse(output.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondZero_printsZeroDivMessageOnlyForDivisionAndModulo() {
        String input = "7\n0\n";
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("7 + 0 = 7"));
        assertTrue(output.contains("7 - 0 = 7"));
        assertTrue(output.contains("7 * 0 = 0"));
        assertTrue(output.contains("除数不能为0，无法进行除法和取余运算。"));

        assertFalse(output.contains(" / 0 = "));
        assertFalse(output.contains(" % 0 = "));
    }

    @Test
    void main_whenFirstNegativeSecondPositive_printsCorrectResults() {
        String input = "-5\n2\n";
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("-5 + 2 = -3"));
        assertTrue(output.contains("-5 - 2 = -7"));
        assertTrue(output.contains("-5 * 2 = -10"));
        assertTrue(output.contains("-5 / 2 = -2"));
        assertTrue(output.contains("-5 % 2 = -1"));
    }

    @Test
    void main_whenBothNegativeSecondNonZero_printsCorrectResults() {
        String input = "-8\n-3\n";
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("-8 + -3 = -11"));
        assertTrue(output.contains("-8 - -3 = -5"));
        assertTrue(output.contains("-8 * -3 = 24"));
        assertTrue(output.contains("-8 / -3 = 2"));
        assertTrue(output.contains("-8 % -3 = -2"));
    }

    @Test
    void main_whenFirstZeroSecondNonZero_printsCorrectResults() {
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("0 + 5 = 5"));
        assertTrue(output.contains("0 - 5 = -5"));
        assertTrue(output.contains("0 * 5 = 0"));
        assertTrue(output.contains("0 / 5 = 0"));
        assertTrue(output.contains("0 % 5 = 0"));
    }

    @Test
    void main_whenBothZero_printsZeroDivMessage() {
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

        String output = out.toString(StandardCharsets.UTF_8);

        assertTrue(output.contains("0 + 0 = 0"));
        assertTrue(output.contains("0 - 0 = 0"));
        assertTrue(output.contains("0 * 0 = 0"));
        assertTrue(output.contains("除数不能为0，无法进行除法和取余运算。"));
        assertFalse(output.contains(" / 0 = "));
        assertFalse(output.contains(" % 0 = "));
    }
}