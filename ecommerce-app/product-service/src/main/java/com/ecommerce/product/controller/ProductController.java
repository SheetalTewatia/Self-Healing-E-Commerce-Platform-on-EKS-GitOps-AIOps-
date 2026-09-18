package com.ecommerce.product.controller;

import com.ecommerce.product.model.Product;
import com.ecommerce.product.service.ProductService;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
@CrossOrigin(origins = "*")
public class ProductController {

    private final ProductService productService;
    private final MongoTemplate mongoTemplate;

    public ProductController(ProductService productService, MongoTemplate mongoTemplate) {
        this.productService = productService;
        this.mongoTemplate = mongoTemplate;
    }

    @GetMapping("/db-info")
    public ResponseEntity<Map<String, Object>> dbInfo() {
        Map<String, Object> info = new LinkedHashMap<>();
        try {
            mongoTemplate.executeCommand("{ ping: 1 }");
            info.put("service",    "product-service");
            info.put("database",   mongoTemplate.getDb().getName());
            info.put("collection", "products");
            info.put("documents",  mongoTemplate.getCollection("products").countDocuments());
            info.put("mongoStatus","CONNECTED");
            info.put("timestamp",  LocalDateTime.now().toString());
            info.put("indexes",    "category field is indexed for fast category filter queries");
        } catch (Exception e) {
            info.put("mongoStatus", "DISCONNECTED");
            info.put("error", e.getMessage());
        }
        return ResponseEntity.ok(info);
    }

    @GetMapping
    public ResponseEntity<List<Product>> getAll(
            @RequestParam(required = false) String category) {
        if (category != null) return ResponseEntity.ok(productService.getByCategory(category));
        return ResponseEntity.ok(productService.getAllProducts());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getById(@PathVariable String id) {
        return productService.getById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Product> create(@RequestBody Product product) {
        return ResponseEntity.status(HttpStatus.CREATED).body(productService.create(product));
    }

    // Called internally by Order Service to reduce stock when order is placed
    @PutMapping("/{id}/stock/reduce")
    public ResponseEntity<?> reduceStock(@PathVariable String id, @RequestBody Map<String, Integer> body) {
        boolean ok = productService.reduceStock(id, body.get("quantity"));
        if (!ok) return ResponseEntity.badRequest().body(Map.of("error", "Insufficient stock or product not found"));
        return ResponseEntity.ok(Map.of("message", "Stock updated"));
    }
}
