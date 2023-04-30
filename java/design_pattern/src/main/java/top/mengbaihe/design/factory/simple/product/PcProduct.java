package top.mengbaihe.design.factory.simple.product;

import top.mengbaihe.design.factory.simple.product.Product;

public class PcProduct implements Product {
    @Override
    public double getPrice() {
        return 9999.99;
    }

    @Override
    public String getName() {
        return "外星人电脑";
    }
}
