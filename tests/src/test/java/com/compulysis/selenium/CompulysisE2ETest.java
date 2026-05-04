package com.compulysis.selenium;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;

public class CompulysisE2ETest extends SeleniumTestBase {

    @Test
    void loginPageShowsBranding() {
        openLogin();
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='login-page']")).isDisplayed());
        Assertions.assertTrue(driver.getPageSource().contains("Compulysis"));
    }

    @Test
    void loginFormFieldsAreVisible() {
        openLogin();
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='login-email']")).isDisplayed());
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='login-password']")).isDisplayed());
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='login-submit']")).isDisplayed());
    }

    @Test
    void loginPasswordToggleChangesFieldType() {
        openLogin();
        WebElement passwordField = driver.findElement(By.cssSelector("[data-testid='login-password']"));
        Assertions.assertEquals("password", passwordField.getAttribute("type"));

        driver.findElement(By.cssSelector("[data-testid='toggle-login-password']")).click();
        Assertions.assertEquals("text", passwordField.getAttribute("type"));
    }

    @Test
    void registerTabRevealsRegistrationForm() {
        openLogin();
        driver.findElement(By.cssSelector("[data-testid='register-tab']")).click();

        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='register-name']")).isDisplayed());
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='register-email']")).isDisplayed());
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='register-password']")).isDisplayed());
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='register-confirm-password']")).isDisplayed());
    }

    @Test
    void registerValidationRejectsMismatchedPasswords() {
        openLogin();
        driver.findElement(By.cssSelector("[data-testid='register-tab']")).click();
        driver.findElement(By.cssSelector("[data-testid='register-name']")).sendKeys("Dr. Test User");
        driver.findElement(By.cssSelector("[data-testid='register-email']")).sendKeys("test.user@example.com");
        new Select(driver.findElement(By.cssSelector("[data-testid='register-specialization']"))).selectByVisibleText("Clinical Psychology");
        driver.findElement(By.cssSelector("[data-testid='register-institution']")).sendKeys("Test Hospital");
        driver.findElement(By.cssSelector("[data-testid='register-password']")).sendKeys("password123");
        driver.findElement(By.cssSelector("[data-testid='register-confirm-password']")).sendKeys("different123");
        driver.findElement(By.cssSelector("[data-testid='register-submit']")).click();

        WebElement errorBanner = waitFor(30).until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='auth-error']")));
        Assertions.assertTrue(errorBanner.getText().contains("Passwords do not match"));
    }

    @Test
    void forgotPasswordFlowShowsConfirmation() {
        openLogin();
        driver.findElement(By.cssSelector("[data-testid='forgot-password-tab']")).click();
        driver.findElement(By.cssSelector("[data-testid='forgot-email']")).sendKeys(TEST_EMAIL);
        driver.findElement(By.cssSelector("[data-testid='forgot-submit']")).click();

        WebElement successBanner = waitFor(60).until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='auth-success']")));
        Assertions.assertTrue(successBanner.getText().contains("Password reset instructions"));
    }

    @Test
    void successfulLoginReachesDashboard() {
        login();
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='dashboard-page']")).isDisplayed());
        Assertions.assertTrue(driver.getPageSource().contains("Welcome back"));
    }

    @Test
    void dashboardMetricsRender() {
        login();
        Assertions.assertTrue(driver.getPageSource().contains("My Active Patients"));
        Assertions.assertTrue(driver.getPageSource().contains("High Risk Cases"));
        Assertions.assertTrue(driver.getPageSource().contains("This Week's Assessments"));
        Assertions.assertTrue(driver.getPageSource().contains("Model Accuracy"));
    }

    @Test
    void logoutReturnsToLoginPage() {
        login();
        driver.findElement(By.cssSelector("[data-testid='logout-button']")).click();
        waitFor(30).until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("[data-testid='login-page']")));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='login-page']")).isDisplayed());
    }

    @Test
    void patientManagementPageLoads() {
        login();
        goTo("nav-patients", "patients-page");
        Assertions.assertTrue(driver.getPageSource().contains("Patient Management"));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='patient-search']")).isDisplayed());
    }

    @Test
    void patientSearchFiltersResults() {
        login();
        goTo("nav-patients", "patients-page");
        WebElement searchInput = driver.findElement(By.cssSelector("[data-testid='patient-search']"));
        searchInput.clear();
        searchInput.sendKeys("zzzz-no-match");

        waitFor(15).until(currentDriver -> currentDriver.getPageSource().contains("No active patients found"));
        Assertions.assertTrue(driver.getPageSource().contains("No active patients found"));
    }

    @Test
    void assessmentPageLoads() {
        login();
        goTo("nav-assessment", "assessment-page");
        Assertions.assertTrue(driver.getPageSource().contains("OCD Symptom Assessment"));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='assessment-page']")).isDisplayed());
    }

    @Test
    void reportsPageLoads() {
        login();
        goTo("nav-reports", "reports-page");
        Assertions.assertTrue(driver.getPageSource().contains("Assessment Reports"));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='reports-page']")).isDisplayed());
    }

    @Test
    void modelLabPageLoads() {
        login();
        goTo("nav-model-lab", "model-lab-page");
        Assertions.assertTrue(driver.getPageSource().contains("Select Model for Detailed Analysis"));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='model-lab-page']")).isDisplayed());
    }

    @Test
    void dataExplorerPageLoads() {
        login();
        goTo("nav-data-explorer", "data-explorer-page");
        Assertions.assertTrue(driver.getPageSource().contains("Interactive Data Explorer"));
        Assertions.assertTrue(driver.findElement(By.cssSelector("[data-testid='data-explorer-page']")).isDisplayed());
    }
}