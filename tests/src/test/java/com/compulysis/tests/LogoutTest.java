package com.compulysis.tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Logout Tests")
public class LogoutTest extends BaseTest {

    @BeforeEach
    void loginFirst() {
        TestHelper.login(driver, baseUrl);
    }

    @Test
    @DisplayName("Logout button is present after login")
    void logoutButtonIsPresent() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement logoutBtn = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//button[contains(., 'Logout') or contains(., 'Sign out') or contains(., 'Log out')]" +
                     " | //a[contains(., 'Logout') or contains(., 'Sign out')]")));
        assertTrue(logoutBtn.isDisplayed(), "Logout button should be visible when authenticated");
    }

    @Test
    @DisplayName("Clicking logout redirects to login page")
    void logoutRedirectsToLogin() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement logoutBtn = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//button[contains(., 'Logout') or contains(., 'Sign out') or contains(., 'Log out')]" +
                     " | //a[contains(., 'Logout') or contains(., 'Sign out')]")));
        logoutBtn.click();

        // Should end up back on the login page
        wait.until(driver1 -> {
            String src = driver1.getPageSource();
            return src.contains("password") || driver1.getCurrentUrl().contains("login");
        });
        String pageSource = driver.getPageSource().toLowerCase();
        assertTrue(
            pageSource.contains("password") || driver.getCurrentUrl().contains("login"),
            "After logout, should be back on the login page"
        );
    }
}
