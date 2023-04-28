package top.mengbaihe.design.singleton.safe;

import org.junit.Test;

/**
 * 现成安全的单例模式测试
 */
public class SingleTonTest {

    /**
     * 使用内部匿名类创建多线程-原始模式
     */
    @Test
    public void safeSingleTonTest(){
        // 测试10次
        for (int i = 0; i < 10; i++) {
            // 使用内部匿名类创建多线程
            new Thread(new Runnable() {
                @Override
                public void run() {
                    SingleTon singleTon = SingleTon.getSingleTon();
                    System.out.println(Thread.currentThread().getName() + "--" + singleTon);
                }
            }).start();
        }
        /**
         * 结果一致
         Thread-8--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-6--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-5--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-7--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-9--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-1--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-0--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-2--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-4--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         Thread-3--top.mengbaihe.design.singleton.safe.SingleTon@26b8de03
         */
    }

    /**
     * 使用内部匿名类创建多线程-原始模式
     */
    @Test
    public void safeSingleTonTestLambda(){
        // 测试10次
        for (int i = 0; i < 10; i++) {
            new Thread(() -> {
                SingleTon singleTon = SingleTon.getSingleTon();
                System.out.println(Thread.currentThread().getName() + "--" + singleTon);
            }).start();
        }
        /**
         * 结果一致
         Thread-6--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-5--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-0--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-4--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-7--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-8--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-9--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-2--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-3--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         Thread-1--top.mengbaihe.design.singleton.safe.SingleTon@57bb6374
         */
    }
}
