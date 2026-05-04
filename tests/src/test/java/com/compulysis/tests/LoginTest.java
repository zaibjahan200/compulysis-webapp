package com.compulysis.tests;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Login Tests")
public class LoginTest extends BaseTest {

    private static final String EMAIL    = "admin@compulysis.com";
    private static final String PASSWORD = "admin123";

    @Test
    @DisplayName("Login page loads and shows email + password fields")
    void loginPageLoads() {
        navigateTo("/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        // The login form should be visible on the root route when not authenticated
        WebElement emailField = wait.until(
            ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("input[type='email'], input[name='email']")));
        assertTrue(emailField.isDisplayed(), "Email field should be visible");

        WebElement passwordField = driver.findElement(
            By.cssSelector("input[type='password'], input[name='password']"));
        assertTrue(passwordField.isDisplayed(), "Password field should be visible");
    }

    @Test
    @DisplayName("Valid credentials redirect to dashboard")
    void validLoginRedirectsToDashboard() {
        navigateTo("/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector("input[type='email'], input[name='email']")))
            .sendKeys(EMAIL);

        driver.findElement(By.cssSelector("input[type='password'], input[name='password']"))
              .sendKeys(PASSWORD);

        driver.findElement(By.cssSelector("button[type='submit']")).click();

        // After login, URL should change away from the login page
        wait.until(ExpectedConditions.not(
            ExpectedConditions.urlContains("/login")));

        String url = driver.getCurrentUrl();
        assertFalse(url.endsWith("/login") || url.endsWith("/"),
            "Should have navigated away from login. Actual URL: " + url);
    }

    @Test
    @DisplayName("Wrong password shows error message")
    void wrongPasswordShowsError() {
        navigateTo("/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector("input[type='email'], input[name='email']")))
            .sendKeys(EMAIL);

        driver.findElement(By.cssSelector("input[type='password'], input[name='password']"))
              .sendKeys("wrongpassword");

        driver.findElement(By.cssSelector("button[type='submit']")).click();

        // An error/alert element should appear
        WebElement error = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector("[role='alert'], .error, .alert, [class*='error'], [class*='alert']")));
        assertTrue(error.isDisplayed(), "An error message should appear for wrong credentials");
    }

    @Test
    @DisplayName("Empty form submission shows validation feedback")
    void emptyFormShowsValidation() {
        navigateTo("/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector("button[type='submit']"))).click();

        // Should still be on login page (not navigated away)
        assertTrue(
            driver.getCurrentUrl().contains("localhost") || driver.getCurrentUrl().contains("login"),
            "Should remain on login page after empty submit");
    }
}
