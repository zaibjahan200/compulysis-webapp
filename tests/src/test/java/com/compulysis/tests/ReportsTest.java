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

@DisplayName("Reports Tests")
public class ReportsTest extends BaseTest {

    @BeforeEach
    void loginFirst() {
        TestHelper.login(driver, baseUrl);
    }

    @Test
    @DisplayName("Reports page is reachable")
    void reportsPageLoads() {
        navigateTo("/reports");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("[class*='report'], h1, h2, table")));
        assertTrue(driver.getCurrentUrl().contains("report"),
            "URL should contain 'report'");
    }

    @Test
    @DisplayName("Export button is present on reports page")
    void exportButtonIsPresent() {
        navigateTo("/reports");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement exportBtn = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//button[contains(., 'Export') or contains(., 'Download') or contains(., 'PDF')]")));
        assertTrue(exportBtn.isDisplayed(), "Export/Download button should be visible on reports page");
    }
}
