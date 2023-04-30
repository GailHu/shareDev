package top.mengbaihe.design.factory.simple.product;

import top.mengbaihe.design.factory.simple.product.Product;

public class PhoneProduct implements Product {
    @Override
    public double getPrice() {
        return 3999.98;
    }

    @Override
    public String getName() {
        return "水果手机";
    }
}
