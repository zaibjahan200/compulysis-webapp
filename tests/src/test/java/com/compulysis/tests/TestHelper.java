package com.compulysis.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

/**
 * TestHelper — shared utility methods used across test classes.
 * Not a test itself; just a helper. Keep it stateless.
 */
public class TestHelper {

    public static final String EMAIL    = "admin@compulysis.com";
    public static final String PASSWORD = "admin123";

    /**
     * Performs a full login and waits until the URL changes away from the
     * login/root page, confirming the app has authenticated.
     */
    public static void login(WebDriver driver, String baseUrl) {
        driver.get(baseUrl + "/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(20));

        WebElement email = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector("input[type='email'], input[name='email']")));
        email.clear();
        email.sendKeys(EMAIL);

        driver.findElement(By.cssSelector("input[type='password'], input[name='password']"))
              .sendKeys(PASSWORD);

        driver.findElement(By.cssSelector("button[type='submit']")).click();

        // Wait until we're past the login page
        wait.until(driver1 -> {
            String url = driver1.getCurrentUrl();
            return !url.endsWith("/") && !url.contains("/login");
        });
    }
}
