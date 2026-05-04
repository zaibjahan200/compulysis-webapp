package com.compulysis.selenium;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public abstract class SeleniumTestBase {
    protected static final String BASE_URL = System.getProperty("baseUrl", "http://host.docker.internal:8004");
    protected static final String BACKEND_HEALTH_URL = System.getProperty("backendHealthUrl", "http://host.docker.internal:8003/health");
    protected static final String TEST_EMAIL = "psychologist@compulysis.com";
    protected static final String TEST_PASSWORD = "password123";

    protected WebDriver driver;

    @BeforeAll
    static void waitForServices() throws Exception {
        waitForUrl(BASE_URL);
        waitForUrl(BACKEND_HEALTH_URL);
    }

    @BeforeEach
    void setUpDriver() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--disable-gpu");
        options.addArguments("--window-size=1440,1200");

        driver = new ChromeDriver(options);
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(60));
    }

    @AfterEach
    void tearDownDriver() {
        if (driver != null) {
            driver.quit();
        }
    }

    protected WebDriverWait waitFor(long seconds) {
        return new WebDriverWait(driver, Duration.ofSeconds(seconds));
    }

    protected void openLogin() {
        driver.get(BASE_URL + "/login");
        waitFor(30).until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("[data-testid='login-page']")));
    }

    protected void login() {
        openLogin();
        waitFor(30).until(ExpectedConditions.elementToBeClickable(By.cssSelector("[data-testid='login-email']")));
        driver.findElement(By.cssSelector("[data-testid='login-email']")).sendKeys(TEST_EMAIL);
        driver.findElement(By.cssSelector("[data-testid='login-password']")).sendKeys(TEST_PASSWORD);
        driver.findElement(By.cssSelector("[data-testid='login-submit']")).click();
        waitFor(60).until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("[data-testid='dashboard-page']")));
    }

    protected void goTo(String navTestId, String pageTestId) {
        driver.findElement(By.cssSelector("[data-testid='" + navTestId + "']")).click();
        waitFor(60).until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("[data-testid='" + pageTestId + "']")));
    }

    private static void waitForUrl(String url) throws Exception {
        HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
        HttpRequest request = HttpRequest.newBuilder().uri(URI.create(url)).timeout(Duration.ofSeconds(5)).GET().build();

        long deadline = System.currentTimeMillis() + Duration.ofSeconds(120).toMillis();
        Exception lastError = null;

        while (System.currentTimeMillis() < deadline) {
            try {
                HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
                if (response.statusCode() >= 200 && response.statusCode() < 400) {
                    return;
                }
            } catch (Exception exception) {
                lastError = exception;
            }

            Thread.sleep(2000);
        }

        throw new IllegalStateException("Timed out waiting for " + url, lastError);
    }
}