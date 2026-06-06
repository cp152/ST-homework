import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class Source1Test {

    @Test
    void main_whenSecondNonZero_printsAllOperations() {
        // 测试负数边界值：num1 = -8, num2 = 2
        String input = "-8\n2\n";

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

        assertTrue(s.contains("-8 + 2 = -6"));
        assertTrue(s.contains("-8 - 2 = -10"));
        assertTrue(s.contains("-8 * 2 = -16"));
        assertTrue(s.contains("-8 / 2 = -4"));
        assertTrue(s.contains("-8 % 2 = 0"));
        assertFalse(s.contains("除数不能为0"));
    }

    @Test
    void main_whenSecondZero_printsZeroDivMessage() {
        // 测试除数为0的异常分支
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
}