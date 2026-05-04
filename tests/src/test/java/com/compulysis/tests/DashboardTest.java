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

@DisplayName("Dashboard Tests")
public class DashboardTest extends BaseTest {

    @BeforeEach
    void loginFirst() {
        TestHelper.login(driver, baseUrl);
    }

    @Test
    @DisplayName("Dashboard page loads after login")
    void dashboardLoads() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        // At least one heading or nav link should be present
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("nav, [class*='dashboard'], [class*='sidebar'], h1, h2")));
        assertNotNull(driver.getTitle(), "Page should have a title");
    }

    @Test
    @DisplayName("Dashboard shows risk chart or summary statistics")
    void dashboardShowsStats() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        // Recharts renders SVG; look for svg or a stat card
        List<WebElement> charts = wait.until(driver1 ->
            driver1.findElements(By.cssSelector("svg, [class*='chart'], [class*='stat'], [class*='card']")));
        assertFalse(charts.isEmpty(), "Dashboard should display at least one chart or stat card");
    }

    @Test
    @DisplayName("Navigation sidebar is visible and contains expected links")
    void sidebarHasLinks() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("nav a, [class*='sidebar'] a")));

        List<WebElement> navLinks = driver.findElements(By.cssSelector("nav a, [class*='sidebar'] a"));
        assertTrue(navLinks.size() >= 2, "Sidebar should have at least 2 navigation links");
    }
}
