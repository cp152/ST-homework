
import java.util.Scanner;

public class Source1 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("请输入第一个整数: ");
        int num1 = scanner.nextInt();

        System.out.print("请输入第二个整数: ");
        int num2 = scanner.nextInt();

        System.out.println("\n运算结果如下：");
        System.out.println(num1 + " + " + num2 + " = " + (num1 + num2));
        System.out.println(num1 + " - " + num2 + " = " + (num1 - num2));
        System.out.println(num1 + " * " + num2 + " = " + (num1 * num2));

        // 处理除数为0的情况
        if (num2 != 0) {
            System.out.println(num1 + " / " + num2 + " = " + (num1 / num2));
            System.out.println(num1 + " % " + num2 + " = " + (num1 % num2));
        } else {
            System.out.println("除数不能为0，无法进行除法和取余运算。");
        }

        scanner.close();
    }
}