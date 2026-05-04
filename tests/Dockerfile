# =============================================================================
# tests/Dockerfile  —  Compulysis Selenium Test Runner
#
# Replaces markhobson/maven-chrome (Chrome 91, incompatible with Selenium 4.x
# CDP v124+) with a modern Ubuntu-based image that ships:
#   • Google Chrome 124  (stable channel, pinned)
#   • ChromeDriver 124   (matching version)
#   • OpenJDK 11
#   • Maven 3.9.x
#
# CDP version matrix (keep these in sync):
#   Chrome 124  →  selenium-devtools-v124  →  Selenium 4.23.x  ✓
#   Chrome 91   →  selenium-devtools-v91   →  Selenium 3.x only ✗
# =============================================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        wget \
        gnupg \
        ca-certificates \
        unzip \
        openjdk-11-jdk-headless \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libdbus-1-3 \
        libgdk-pixbuf2.0-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# ── Google Chrome 124 (stable) ─────────────────────────────────────────────────
# We pin a specific .deb so the image is reproducible and the CDP version
# in pom.xml (selenium-devtools-v124) always matches.
ARG CHROME_VERSION=124.0.6367.207-1
RUN wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb" \
        -O /tmp/chrome.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# ── ChromeDriver 124 ───────────────────────────────────────────────────────────
ARG CHROMEDRIVER_VERSION=124.0.6367.207
RUN wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
        -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# ── Maven 3.9.8 ────────────────────────────────────────────────────────────────
ARG MAVEN_VERSION=3.9.8
RUN wget -q "https://downloads.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \
        -O /tmp/maven.tar.gz \
    && tar -xzf /tmp/maven.tar.gz -C /opt \
    && ln -s /opt/apache-maven-${MAVEN_VERSION}/bin/mvn /usr/local/bin/mvn \
    && rm /tmp/maven.tar.gz

# ── Environment ────────────────────────────────────────────────────────────────
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:/usr/local/bin:${PATH}"

# Tell WebDriverManager / Selenium to use the pre-installed driver
ENV WEBDRIVER_CHROME_DRIVER=/usr/local/bin/chromedriver

# ── Verify versions at build time ─────────────────────────────────────────────
RUN google-chrome --version && chromedriver --version && mvn --version

WORKDIR /workspace
