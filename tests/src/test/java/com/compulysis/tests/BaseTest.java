package com.compulysis.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;

/**
 * BaseTest
 *
 * Shared setup/teardown for all Compulysis Selenium tests.
 *
 * Chrome flags required for Docker (no display, no sandbox):
 *   --headless=new         new headless mode (Chrome 112+), not the legacy --headless
 *   --no-sandbox           required when running as root inside a container
 *   --disable-dev-shm-usage  /dev/shm is often tiny in Docker; use /tmp instead
 *   --disable-gpu          no GPU in headless containers
 *   --remote-allow-origins=*  needed for Selenium 4 CDP communication
 */
public abstract class BaseTest {

    protected WebDriver driver;
    protected String baseUrl;

    @BeforeEach
    public void setUp() {
        baseUrl = System.getProperty("baseUrl", "http://localhost:8004");

        // If WEBDRIVER_CHROME_DRIVER env var is set (our Docker image sets it),
        // WebDriverManager will skip the download and use the pre-installed binary.
        String preInstalledDriver = System.getenv("WEBDRIVER_CHROME_DRIVER");
        if (preInstalledDriver != null && !preInstalledDriver.isEmpty()) {
            System.setProperty("webdriver.chrome.driver", preInstalledDriver);
        } else {
            // Fallback: let WebDriverManager download a matching ChromeDriver.
            // This path is used when running tests locally (not in Docker).
            WebDriverManager.chromedriver().setup();
        }

        ChromeOptions options = buildChromeOptions();
        driver = new ChromeDriver(options);

        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        driver.manage().window().maximize();
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    /**
     * Build ChromeOptions from the chromeArgs system property (set in pom.xml)
     * or fall back to a safe set of defaults.
     */
    private ChromeOptions buildChromeOptions() {
        ChromeOptions options = new ChromeOptions();

        String rawArgs = System.getProperty("chromeArgs", "");
        if (!rawArgs.isEmpty()) {
            List<String> args = Arrays.asList(rawArgs.split(","));
            options.addArguments(args);
        } else {
            // Hard defaults — always safe for Docker
            options.addArguments(
                "--headless=new",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--remote-allow-origins=*"
            );
        }

        return options;
    }

    /** Navigate to a path relative to baseUrl. */
    protected void navigateTo(String path) {
        driver.get(baseUrl + path);
    }
}
