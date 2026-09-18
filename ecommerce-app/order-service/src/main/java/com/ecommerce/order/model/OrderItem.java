package com.ecommerce.order.model;

public class OrderItem {
    private String productId;
    private String productName;
    private int quantity;
    private double price;

    public OrderItem() {}
    public OrderItem(String productId, String productName, int quantity, double price) {
        this.productId = productId; this.productName = productName;
        this.quantity = quantity; this.price = price;
    }

    public String getProductId() { return productId; }
    public void setProductId(String p) { this.productId = p; }
    public String getProductName() { return productName; }
    public void setProductName(String p) { this.productName = p; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int q) { this.quantity = q; }
    public double getPrice() { return price; }
    public void setPrice(double p) { this.price = p; }
}
