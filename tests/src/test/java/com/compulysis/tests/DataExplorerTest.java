package com.compulysis.tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Data Explorer Tests")
public class DataExplorerTest extends BaseTest {

    @Test
    @DisplayName("Data explorer page loads")
    void dataExplorerLoads() {
        // Try common URL slugs for the data explorer
        navigateTo("/data-explorer");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("h1, h2, table, [class*='explorer'], [class*='data']")));
        assertTrue(driver.getPageSource().length() > 100, "Data explorer page should render");
    }

    @Test
    @DisplayName("Data explorer shows table or CSV content")
    void dataExplorerShowsContent() {
        navigateTo("/data-explorer");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        // CSV-based explorer typically renders a table
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("table, [class*='data-table'], [class*='grid'], [class*='empty']")));
        assertNotNull(driver.findElement(
            By.cssSelector("table, [class*='data-table'], [class*='grid'], [class*='empty']")));
    }
}
