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

@DisplayName("Patient List Tests")
public class PatientListTest extends BaseTest {

    @Test
    @DisplayName("Patients page loads")
    void patientsPageLoads() {
        navigateTo("/patients");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.cssSelector("table, [class*='patient'], h1, h2")));
        assertTrue(driver.getCurrentUrl().contains("patient"),
            "URL should contain 'patient'");
    }

    @Test
    @DisplayName("Patient list renders rows or empty state")
    void patientListRendersContent() {
        navigateTo("/patients");
        // Either a table with rows, or an empty-state message
        List<WebElement> rows = driver.findElements(By.cssSelector("tbody tr, [class*='patient-row']"));
        List<WebElement> emptyState = driver.findElements(
            By.cssSelector("[class*='empty'], [class*='no-data'], [class*='placeholder']"));
        assertTrue(!rows.isEmpty() || !emptyState.isEmpty(),
            "Should show patient rows or an empty state message");
    }

    @Test
    @DisplayName("Add patient button is present")
    void addPatientButtonPresent() {
        navigateTo("/patients");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement addBtn = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//button[contains(., 'Add') or contains(., 'New') or contains(., 'Create')]")));
        assertTrue(addBtn.isDisplayed(), "Add/New Patient button should be visible");
    }
}
