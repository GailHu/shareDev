package top.mengbaihe.design.factory.simple.product;

/**
 * 产品类
 */
public interface Product {
    double price = 0;
    String name = null;

    /**
     * 获取价格
     * @return 价格
     */
    double getPrice();

    /**
     * 获取名称
     * @return 名称
     */
    String getName();

}
