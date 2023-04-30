package top.mengbaihe.design.factory.simple;

import top.mengbaihe.design.factory.simple.product.PcProduct;
import top.mengbaihe.design.factory.simple.product.PhoneProduct;
import top.mengbaihe.design.factory.simple.product.Product;

/**
 * 简单工厂模式，用于生产对应实例
 *      当增加产品时，只需要添加对应的实现，修改当前类即可
 */
public class ProductFactory {

    public static Product getProduct(String name){
        Product product = null;
        switch (name){
            case "电脑":
                product = new PcProduct();
                break;
            case "手机":
                product = new PhoneProduct();
                break;
            default:
                break;
        }
        return product;
    }
}
