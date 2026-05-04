package com.compulysis.tests;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Assessment Tests")
public class AssessmentTest extends BaseTest {

    @Test
    @DisplayName("Assessments page is reachable")
    void assessmentsPageLoads() {
        navigateTo("/assessments");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("table, [class*='assessment'], h1, h2")));
        assertTrue(driver.getPageSource().length() > 100,
            "Assessments page should have content");
    }

    @Test
    @DisplayName("Assessment list shows content or empty state")
    void assessmentListRendersContent() {
        navigateTo("/assessments");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("tbody tr, [class*='assessment-row'], [class*='empty'], [class*='no-data']")));

        List<WebElement> rows = driver.findElements(By.cssSelector("tbody tr, [class*='assessment-row']"));
        List<WebElement> emptyState = driver.findElements(
            By.cssSelector("[class*='empty'], [class*='no-data']"));
        assertTrue(!rows.isEmpty() || !emptyState.isEmpty(),
            "Should show assessments or an empty state");
    }
}
