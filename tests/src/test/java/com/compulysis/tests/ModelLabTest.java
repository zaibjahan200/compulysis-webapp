package com.compulysis.tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Model Lab Tests")
public class ModelLabTest extends BaseTest {

    @BeforeEach
    void loginFirst() {
        TestHelper.login(driver, baseUrl);
    }

    @Test
    @DisplayName("Model lab page loads")
    void modelLabLoads() {
        navigateTo("/model-lab");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("h1, h2, [class*='model'], [class*='lab']")));
        assertTrue(driver.getPageSource().length() > 100, "Model lab page should render content");
    }

    @Test
    @DisplayName("Model lab shows comparison elements or metrics")
    void modelLabShowsMetrics() {
        navigateTo("/model-lab");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        // Model lab should show charts, tables, or metric cards
        List<WebElement> elements = wait.until(driver1 ->
            driver1.findElements(By.cssSelector(
                "svg, table, [class*='metric'], [class*='card'], [class*='model']")));
        assertFalse(elements.isEmpty(), "Model lab should display at least one metric, chart, or card");
    }
}
