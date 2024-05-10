package gail.study;

import java.lang.management.ManagementFactory;


/**
 * Hello world!
 */
public class App {
    public static boolean isDebug() {
        for (String arg : ManagementFactory.getRuntimeMXBean().getInputArguments()) {
            if (arg.contains("jdwp")) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        if (isDebug()) {
            System.out.println("Debug mode is enabled.");
        } else {
            System.out.println("Debug mode is not enabled.");
        }
    }

}
