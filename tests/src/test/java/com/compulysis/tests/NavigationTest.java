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

@DisplayName("Navigation Tests")
public class NavigationTest extends BaseTest {

    @BeforeEach
    void loginFirst() {
        TestHelper.login(driver, baseUrl);
    }

    @Test
    @DisplayName("Clicking Patients nav link navigates to patients page")
    void clickPatientsNavLink() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement patientsLink = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//a[contains(., 'Patient') or contains(@href, 'patient')]")));
        patientsLink.click();
        wait.until(ExpectedConditions.urlContains("patient"));
        assertTrue(driver.getCurrentUrl().contains("patient"),
            "URL should contain 'patient' after clicking the Patients link");
    }

    @Test
    @DisplayName("Clicking Dashboard nav link navigates back to dashboard")
    void clickDashboardNavLink() {
        // First go somewhere else
        navigateTo("/patients");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        WebElement dashLink = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//a[contains(., 'Dashboard') or contains(@href, 'dashboard')]")));
        dashLink.click();
        wait.until(ExpectedConditions.urlContains("dashboard"));
        assertTrue(driver.getCurrentUrl().contains("dashboard"),
            "URL should contain 'dashboard' after clicking the Dashboard link");
    }
}
