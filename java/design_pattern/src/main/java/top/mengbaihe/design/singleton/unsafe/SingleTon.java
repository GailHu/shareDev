package top.mengbaihe.design.singleton.unsafe;


/**
 * 单例模式-线程不安全，省内存
 */
public class SingleTon {
    /*
    定义：确保一个类只有一个实例
        有两种方式
            第一种是定义静态变量直接初始化，这样在类加载的时候就会创建单例对象
                优点是线程安全的；
                缺点是可能在整个程序运行期间，这个类都不会用到，浪费内存；
            第二种方式是定义变量时先留空，第一次获取时创建对象，
                默认不是线程安全的；可以使用sync关键字加锁保证现成安全；
                优点是第一次用的时候才会创建
     */
    // 定义当前对象为static final
    private static SingleTon singleTon = null;
    // 私有化构造方法
    private SingleTon() {
    }

    // 声明线程不安全的获取实例对象方法
    public static SingleTon getSingleTonUnSafe() {
        // 检查是否是第一次调用，如果第一次调用，需要创建对象
        if(singleTon == null){
            singleTon = new SingleTon();
        }
        return singleTon;
    }
    // 声明线程安全的获取实例对象方法
    public static synchronized SingleTon getSingleTonSafe() {
        // 检查是否是第一次调用，如果第一次调用，需要创建对象
        if(singleTon == null){
            singleTon = new SingleTon();
        }
        return singleTon;
    }
    // 如果还有其它方法，也尽量是静态的
    public static void doSomething(){

    }
}
