package com.ecommerce.product.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

/**
 * MongoDB document structure:
 * {
 *   "_id":         "64ab...",
 *   "name":        "MacBook Pro",
 *   "description": "...",
 *   "price":       1999.99,
 *   "stock":       15,
 *   "category":    "Electronics",   ← @Indexed → fast findByCategory queries
 *   "imageUrl":    "https://..."
 * }
 */
@Document(collection = "products")
public class Product {
    @Id
    private String id;

    private String name;
    private String description;
    private double price;
    private int stock;
    @Indexed                               // Index on category for fast filter queries
    private String category;
    private String imageUrl;

    public Product() {}
    public Product(String name, String description, double price, int stock, String category, String imageUrl) {
        this.name = name; this.description = description; this.price = price;
        this.stock = stock; this.category = category; this.imageUrl = imageUrl;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }
    public String getCategory() { return category; }
    public void setCategory(String c) { this.category = c; }
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String url) { this.imageUrl = url; }
}
