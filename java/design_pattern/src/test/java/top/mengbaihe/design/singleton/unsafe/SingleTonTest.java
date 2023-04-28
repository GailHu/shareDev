package top.mengbaihe.design.singleton.unsafe;

import org.junit.Test;

/**
 * 默认不安全的单例模式测试
 */
public class SingleTonTest {
    /**
     * 内部类实现多线程，集成子Thread
     */
    public class UnsafeSingTonThread extends Thread{
        @Override
        public void run() {
            // 获取不安全的单例对象，并打印线程和对象
            SingleTon singleTon = SingleTon.getSingleTonUnSafe();
            System.out.println(Thread.currentThread().getName() + "--" + singleTon);
        }
    }

    /**
     * 内部类实现多线程，集成子Thread
     */
    public class UnsafeSingTonRunnable implements Runnable{
        @Override
        public void run() {
            // 获取不安全的单例对象，并打印线程和对象
            SingleTon singleTon = SingleTon.getSingleTonSafe();
            System.out.println(Thread.currentThread().getName() + "--" + singleTon);
        }
    }
    @Test
    public void unsafeTest() throws InterruptedException {
        for (int i = 0; i < 10; i++) {
            UnsafeSingTonThread unsafeSingTonThread = new UnsafeSingTonThread();
            unsafeSingTonThread.start();
        }
        Thread.sleep(5000);
        /*
            Thread-7--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-3--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-0--top.mengbaihe.design.singleton.unsafe.SingleTon@ebd672d
            Thread-8--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-9--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-4--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-5--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-6--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-1--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
            Thread-2--top.mengbaihe.design.singleton.unsafe.SingleTon@5f0f5205
         */
    }
    @Test
    public void safeTest() throws InterruptedException {
        for (int i = 0; i < 10; i++) {
            Thread thread = new Thread(new UnsafeSingTonRunnable());
            thread.start();
        }
        Thread.sleep(5000);
        /*
         * 无论多少次，都一样
         Thread-6--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-0--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-3--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-4--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-2--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-7--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-5--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-1--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-9--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         Thread-8--top.mengbaihe.design.singleton.unsafe.SingleTon@384067e5
         */
    }
}
