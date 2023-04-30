package top.mengbaihe.design.factory.simple;

import org.junit.Assert;
import org.junit.Test;
import top.mengbaihe.design.factory.simple.product.Product;

/**
 * 简单工厂模式测试类
 */
public class ProductFactoryTest {

    @Test
    public void test(){
        Product pc = ProductFactory.getProduct("电脑");
        Assert.assertEquals("外星人电脑", pc.getName());
        Assert.assertEquals(9999.99, pc.getPrice(), 0);
        Product phone = ProductFactory.getProduct("手机");
        Assert.assertEquals("水果手机", phone.getName());
        Assert.assertEquals(3999.98, phone.getPrice(), 0);
    }
}
