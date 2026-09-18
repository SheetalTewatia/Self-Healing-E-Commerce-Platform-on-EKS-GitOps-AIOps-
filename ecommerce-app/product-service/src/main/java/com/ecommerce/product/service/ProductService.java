package com.ecommerce.product.service;

import com.ecommerce.product.model.Product;
import com.ecommerce.product.repository.ProductRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class ProductService implements CommandLineRunner {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    // Seed demo data on startup if collection is empty
    @Override
    public void run(String... args) {
        if (productRepository.count() == 0) {
            productRepository.saveAll(List.of(
                new Product("MacBook Pro 14\"", "Apple M3 chip, 16GB RAM, 512GB SSD", 1999.99, 15, "Electronics",
                    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"),
                new Product("iPhone 15 Pro", "6.1-inch display, 48MP camera, Titanium design", 999.99, 30, "Electronics",
                    "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400"),
                new Product("Sony WH-1000XM5", "Industry-leading noise cancelling wireless headphones", 349.99, 50, "Electronics",
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"),
                new Product("Nike Air Max 270", "Lightweight running shoes with Air cushioning", 149.99, 100, "Fashion",
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"),
                new Product("Levi's 501 Jeans", "Classic straight fit denim jeans", 69.99, 200, "Fashion",
                    "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"),
                new Product("The Clean Coder", "A Code of Conduct for Professional Programmers by Robert Martin", 39.99, 80, "Books",
                    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400"),
                new Product("Kubernetes in Action", "Manning guide to running apps in Kubernetes", 49.99, 60, "Books",
                    "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400"),
                new Product("Samsung 4K Monitor 27\"", "UHD IPS panel, 144Hz, HDR600", 599.99, 20, "Electronics",
                    "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400")
            ));
        }
    }

    public List<Product> getAllProducts() { return productRepository.findAll(); }
    public List<Product> getByCategory(String category) { return productRepository.findByCategory(category); }
    public Optional<Product> getById(String id) { return productRepository.findById(id); }

    public Product create(Product product) { return productRepository.save(product); }

    public boolean reduceStock(String id, int quantity) {
        Optional<Product> opt = productRepository.findById(id);
        if (opt.isEmpty()) return false;
        Product p = opt.get();
        if (p.getStock() < quantity) return false;
        p.setStock(p.getStock() - quantity);
        productRepository.save(p);
        return true;
    }
}
