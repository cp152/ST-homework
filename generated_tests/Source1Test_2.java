import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.assertEquals;

class Source1Test {

    private String runWithInput(String input) {
        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            System.setIn(new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8)));
            System.setOut(new PrintStream(out, true, StandardCharsets.UTF_8));
            Source1.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }
        return out.toString(StandardCharsets.UTF_8);
    }

    @Test
    void main_withPositiveNumbers_printsAllOperations() {
        String input = "5\n3\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n5 + 3 = 8\n5 - 3 = 2\n5 * 3 = 15\n5 / 3 = 1\n5 % 3 = 2\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withZeroDivisor_printsZeroDivisionMessage() {
        String input = "5\n0\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n5 + 0 = 5\n5 - 0 = 5\n5 * 0 = 0\n除数不能为0，无法进行除法和取余运算。\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withNegativeNumbers_printsCorrectResults() {
        String input = "-5\n2\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n-5 + 2 = -3\n-5 - 2 = -7\n-5 * 2 = -10\n-5 / 2 = -2\n-5 % 2 = -1\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withNegativeDividendAndZeroDivisor_printsMessage() {
        String input = "-5\n0\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n-5 + 0 = -5\n-5 - 0 = -5\n-5 * 0 = 0\n除数不能为0，无法进行除法和取余运算。\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withZeroDividendAndNonZeroDivisor_printsZeroResults() {
        String input = "0\n5\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n0 + 5 = 5\n0 - 5 = -5\n0 * 5 = 0\n0 / 5 = 0\n0 % 5 = 0\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withMaxIntegerDividendAndOneDivisor_printsCorrectResults() {
        String input = "2147483647\n1\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n2147483647 + 1 = 2147483648\n2147483647 - 1 = 2147483646\n2147483647 * 1 = 2147483647\n2147483647 / 1 = 2147483647\n2147483647 % 1 = 0\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withMinIntegerDividendAndOneDivisor_printsCorrectResults() {
        String input = "-2147483648\n1\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n-2147483648 + 1 = -2147483647\n-2147483648 - 1 = -2147483649\n-2147483648 * 1 = -2147483648\n-2147483648 / 1 = -2147483648\n-2147483648 % 1 = 0\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withMinIntegerDividendAndMinusOneDivisor_printsCorrectResults() {
        String input = "-2147483648\n-1\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n-2147483648 + -1 = -2147483649\n-2147483648 - -1 = -2147483647\n-2147483648 * -1 = 2147483648\n-2147483648 / -1 = -2147483648\n-2147483648 % -1 = 0\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withMaxIntegerDividendAndMinusOneDivisor_printsCorrectResults() {
        String input = "2147483647\n-1\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n2147483647 + -1 = 2147483646\n2147483647 - -1 = 2147483648\n2147483647 * -1 = -2147483647\n2147483647 / -1 = -2147483647\n2147483647 % -1 = 0\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withBothZero_printsZeroDivisionMessage() {
        String input = "0\n0\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n0 + 0 = 0\n0 - 0 = 0\n0 * 0 = 0\n除数不能为0，无法进行除法和取余运算。\n";
        assertEquals(expected, runWithInput(input));
    }

    @Test
    void main_withLargePositiveDivisor_printsCorrectResults() {
        String input = "1\n2147483647\n";
        String expected = "请输入第一个整数: 请输入第二个整数: \n\n运算结果如下：\n1 + 2147483647 = 2147483648\n1 - 2147483647 = -2147483646\n1 * 2147483647 = 2147483647\n1 / 2147483647 = 0\n1 % 2147483647 = 1\n";
        assertEquals(expected, runWithInput(input));
    }
}