import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class Source1Test {

    @Test
    void main_whenSecondNonZero_printsCorrectArithmeticResults() {
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

        String output = out.toString(StandardCharsets.UTF_8);
        assertTrue(output.contains("8 + 2 = 10"));
        assertTrue(output.contains("8 - 2 = 6"));
        assertTrue(output.contains("8 * 2 = 16"));
        assertTrue(output.contains("8 / 2 = 4"));
        assertTrue(output.contains("8 % 2 = 0"));
        assertFalse(output.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondIsZero_printsDivisionByZeroMessageAndSkipsDivMod() {
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

        String output = out.toString(StandardCharsets.UTF_8);
        assertTrue(output.contains("8 + 0 = 8"));
        assertTrue(output.contains("8 - 0 = 8"));
        assertTrue(output.contains("8 * 0 = 0"));
        assertTrue(output.contains("除数不能为0，无法进行除法和取余运算。"));
        assertFalse(output.contains("8 / 0 = "));
        assertFalse(output.contains("8 % 0 = "));
    }

    @Test
    void main_whenFirstIsNegativeSecondPositive_printsCorrectResults() {
        String input = "-5\n3\n";
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
        assertTrue(output.contains("-5 + 3 = -2"));
        assertTrue(output.contains("-5 - 3 = -8"));
        assertTrue(output.contains("-5 * 3 = -15"));
        assertTrue(output.contains("-5 / 3 = -1"));
        assertTrue(output.contains("-5 % 3 = -2"));
    }

    @Test
    void main_whenFirstPositiveSecondNegative_printsCorrectResults() {
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

        String output = out.toString(StandardCharsets.UTF_8);
        assertTrue(output.contains("7 + -2 = 5"));
        assertTrue(output.contains("7 - -2 = 9"));
        assertTrue(output.contains("7 * -2 = -14"));
        assertTrue(output.contains("7 / -2 = -3"));
        assertTrue(output.contains("7 % -2 = 1"));
    }

    @Test
    void main_whenBothNegativeSecondNonZero_printsCorrectResults() {
        String input = "-10\n-4\n";
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
        assertTrue(output.contains("-10 + -4 = -14"));
        assertTrue(output.contains("-10 - -4 = -6"));
        assertTrue(output.contains("-10 * -4 = 40"));
        assertTrue(output.contains("-10 / -4 = 2"));
        assertTrue(output.contains("-10 % -4 = -2"));
    }

    @Test
    void main_whenSecondIsOne_printsSameValuesForDivAndMod() {
        String input = "123\n1\n";
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
        assertTrue(output.contains("123 / 1 = 123"));
        assertTrue(output.contains("123 % 1 = 0"));
    }

    @Test
    void main_whenSecondIsMinusOne_printsCorrectDivAndMod() {
        String input = "456\n-1\n";
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
        assertTrue(output.contains("456 / -1 = -456"));
        assertTrue(output.contains("456 % -1 = 0"));
    }

    @Test
    void main_whenFirstIsZero_printsCorrectResults() {
        String input = "0\n7\n";
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
        assertTrue(output.contains("0 + 7 = 7"));
        assertTrue(output.contains("0 - 7 = -7"));
        assertTrue(output.contains("0 * 7 = 0"));
        assertTrue(output.contains("0 / 7 = 0"));
        assertTrue(output.contains("0 % 7 = 0"));
    }

    @Test
    void main_whenBothZero_printsZeroForAddSubMulAndDivisionByZeroMessage() {
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
        assertFalse(output.contains("0 / 0 = "));
        assertFalse(output.contains("0 % 0 = "));
    }

    @Test
    void main_whenInputsAreEdgeInts_printsActualJavaOverflowBehaviour() {
        // Integer.MAX_VALUE + 1 overflows to Integer.MIN_VALUE
        // Integer.MAX_VALUE - 1 is fine
        // Integer.MIN_VALUE - 1 overflows to Integer.MAX_VALUE
        // This test verifies actual Java int overflow behavior
        String input = Integer.MAX_VALUE + "\n1\n";
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
        // With overflow: Integer.MAX_VALUE + 1 = Integer.MIN_VALUE
        assertTrue(output.contains(Integer.MAX_VALUE + " + 1 = " + (Integer.MAX_VALUE + 1)));
        assertTrue(output.contains(Integer.MAX_VALUE + " - 1 = " + (Integer.MAX_VALUE - 1)));
        assertTrue(output.contains(Integer.MAX_VALUE + " * 1 = " + Integer.MAX_VALUE));
        assertTrue(output.contains(Integer.MAX_VALUE + " / 1 = " + Integer.MAX_VALUE));
        assertTrue(output.contains(Integer.MAX_VALUE + " % 1 = 0"));
    }

    @Test
    void main_whenLargeNegativeOverflow_printsActualJavaOverflowBehaviour() {
        // Integer.MIN_VALUE - 1 = Integer.MAX_VALUE due to overflow
        String input = Integer.MIN_VALUE + "\n1\n";
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
        // Integer.MIN_VALUE - 1 = Integer.MAX_VALUE
        assertTrue(output.contains(Integer.MIN_VALUE + " - 1 = " + (Integer.MIN_VALUE - 1)));
        // Integer.MIN_VALUE + 1 = Integer.MIN_VALUE + 1
        assertTrue(output.contains(Integer.MIN_VALUE + " + 1 = " + (Integer.MIN_VALUE + 1)));
        assertTrue(output.contains(Integer.MIN_VALUE + " * 1 = " + Integer.MIN_VALUE));
        assertTrue(output.contains(Integer.MIN_VALUE + " / 1 = " + Integer.MIN_VALUE));
        assertTrue(output.contains(Integer.MIN_VALUE + " % 1 = 0"));
    }

    @Test
    void main_whenInputIsNonInteger_throwsInputMismatchException() {
        String input = "abc\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;

        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));

        try {
            System.setIn(in);
            assertThrows(java.util.InputMismatchException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
    }

    @Test
    void main_whenSecondInputIsNonInteger_throwsInputMismatchException() {
        String input = "10\nxyz\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;

        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));

        try {
            System.setIn(in);
            assertThrows(java.util.InputMismatchException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
    }

    @Test
    void main_whenInputIsFloatingPoint_throwsInputMismatchException() {
        String input = "5.5\n3\n";
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;

        ByteArrayInputStream in = new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8));

        try {
            System.setIn(in);
            assertThrows(java.util.InputMismatchException.class, () -> Source1.main(new String[0]));
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
    }
}