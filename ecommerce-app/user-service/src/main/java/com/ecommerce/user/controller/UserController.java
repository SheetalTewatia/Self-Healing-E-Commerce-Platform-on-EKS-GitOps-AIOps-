package com.ecommerce.user.controller;

import com.ecommerce.user.model.User;
import com.ecommerce.user.service.UserService;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {

    private final UserService userService;
    private final MongoTemplate mongoTemplate;

    public UserController(UserService userService, MongoTemplate mongoTemplate) {
        this.userService = userService;
        this.mongoTemplate = mongoTemplate;
    }

    /**
     * Hit this URL to see live MongoDB connection info:
     * GET http://localhost:8081/api/users/db-info
     * (or via gateway: GET http://localhost:8080/api/users/db-info)
     */
    @GetMapping("/db-info")
    public ResponseEntity<Map<String, Object>> dbInfo() {
        Map<String, Object> info = new LinkedHashMap<>();
        try {
            mongoTemplate.executeCommand("{ ping: 1 }");
            info.put("service",    "user-service");
            info.put("database",   mongoTemplate.getDb().getName());
            info.put("collection", "users");
            info.put("documents",  mongoTemplate.getCollection("users").countDocuments());
            info.put("mongoStatus","CONNECTED");
            info.put("timestamp",  LocalDateTime.now().toString());
            info.put("connectionNote",
                "Spring Boot reads 'spring.data.mongodb.uri' → creates MongoClient → " +
                "UserRepository extends MongoRepository → auto-generates CRUD methods");
        } catch (Exception e) {
            info.put("mongoStatus", "DISCONNECTED");
            info.put("error", e.getMessage());
        }
        return ResponseEntity.ok(info);
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> body) {
        try {
            User user = userService.register(body.get("name"), body.get("email"), body.get("password"));
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(Map.of("userId", user.getId(), "name", user.getName(), "email", user.getEmail()));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> body) {
        try {
            Map<String, String> result = userService.login(body.get("email"), body.get("password"));
            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getUser(@PathVariable String id) {
        return userService.getUserById(id)
                .map(u -> ResponseEntity.ok(Map.of("userId", u.getId(), "name", u.getName(), "email", u.getEmail())))
                .orElse(ResponseEntity.notFound().build());
    }
}
