package com.compulysis.tests;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Backend Health Tests")
public class BackendHealthTest extends BaseTest {

    @Test
    @DisplayName("Backend /health endpoint returns HTTP 200")
    void backendHealthEndpointReturns200() throws Exception {
        String healthUrl = System.getProperty("backendHealthUrl", "http://localhost:8003/health");
        HttpURLConnection conn = (HttpURLConnection) new URL(healthUrl).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        int status = conn.getResponseCode();
        assertEquals(200, status,
            "Backend /health should return 200. Got: " + status + " from " + healthUrl);
    }

    @Test
    @DisplayName("Frontend root page returns a React app shell")
    void frontendRootPageLoads() {
        navigateTo("/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        // React app always mounts into a #root or #app div
        WebElement root = wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("#root, #app, [id='root'], [id='app']")));
        assertNotNull(root, "React root element should exist");
    }
}
