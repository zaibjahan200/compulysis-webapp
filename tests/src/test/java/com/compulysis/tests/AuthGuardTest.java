package com.compulysis.tests;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Auth Guard Tests")
public class AuthGuardTest extends BaseTest {

    // NOTE: BaseTest does NOT log in before these tests — that's intentional.
    // We are verifying that unauthenticated access to protected routes is blocked.

    @Test
    @DisplayName("Accessing /patients without login redirects to login page")
    void patientsRouteIsProtected() {
        navigateTo("/patients");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        // Should be redirected back to login
        wait.until(driver1 -> {
            String url = driver1.getCurrentUrl();
            String src = driver1.getPageSource();
            return url.contains("login") || src.contains("email") || src.contains("password");
        });
        String pageSource = driver.getPageSource().toLowerCase();
        assertTrue(
            driver.getCurrentUrl().contains("login") ||
            pageSource.contains("email") ||
            pageSource.contains("sign in") ||
            pageSource.contains("login"),
            "Unauthenticated access to /patients should redirect to login"
        );
    }

    @Test
    @DisplayName("Accessing /reports without login redirects to login page")
    void reportsRouteIsProtected() {
        navigateTo("/reports");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(driver1 -> {
            String url = driver1.getCurrentUrl();
            String src = driver1.getPageSource();
            return url.contains("login") || src.contains("password");
        });
        String pageSource = driver.getPageSource().toLowerCase();
        assertTrue(
            driver.getCurrentUrl().contains("login") ||
            pageSource.contains("password"),
            "Unauthenticated access to /reports should redirect to login"
        );
    }
}
