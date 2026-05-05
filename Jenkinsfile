// =============================================================================
// Jenkinsfile — Compulysis CI Pipeline
//
// Python-based Selenium test flow:
//   1. Build a dedicated Python + Chrome + ChromeDriver test image from tests/Dockerfile.
//   2. Start the app stack with docker compose.
//   3. Run pytest inside the container and emit JUnit XML for Jenkins.
//   4. Publish the pytest report and email the committer with a summary.
// =============================================================================

pipeline {
    agent any

    environment {
        // Pre-built image from Docker Hub
        TEST_IMAGE = "zaibjahan200/compulysis-test-runner:latest"

        // Fallback recipient if git log cannot find the committer.
        FALLBACK_EMAIL = "jahanzaibparacha.32@gmail.com"  // ← change this to your team email
    }

    stages {



        // ── Stage 2: Start the application ────────────────────────────────────
        stage('Build') {
            steps {
                sh 'docker compose down --remove-orphans || true'
                sh 'docker compose pull || true'
                sh 'docker compose up -d --remove-orphans'
            }
        }

        // ── Stage 3: Wait for health + run Selenium tests ─────────────────────
        stage('Test') {
            steps {
                sh '''
                    set -e

                    # ── Wait for backend health endpoint ──────────────────────
                    echo "Waiting for backend at http://localhost:8003/health ..."
                    ready=false
                    for attempt in $(seq 1 36); do
                        if curl -fsS "http://localhost:8003/health" >/dev/null 2>&1; then
                            ready=true
                            break
                        fi
                        echo "  attempt ${attempt}/36 — sleeping 5s"
                        sleep 5
                    done
                    if [ "${ready}" != "true" ]; then
                        echo "ERROR: Backend did not become healthy within 3 minutes."
                        docker compose logs backend
                        exit 1
                    fi
                    echo "Backend is healthy."

                    # ── Wait for frontend ─────────────────────────────────────
                    echo "Waiting for frontend at http://localhost:8004 ..."
                    ready=false
                    for attempt in $(seq 1 12); do
                        if curl -fsS "http://localhost:8004" >/dev/null 2>&1; then
                            ready=true
                            break
                        fi
                        echo "  attempt ${attempt}/12 — sleeping 5s"
                        sleep 5
                    done
                    if [ "${ready}" != "true" ]; then
                        echo "ERROR: Frontend did not become available within 1 minute."
                        docker compose logs frontend
                        exit 1
                    fi
                    echo "Frontend is available."

                    # ── Run pytest Selenium tests ──────────────────────────────
                    # Key flags:
                    #   --add-host lets the container reach the host's ports
                    docker run --rm \
                        --add-host=host.docker.internal:host-gateway \
                        -v "${WORKSPACE}/selenium_tests:/workspace" \
                        --shm-size=1g \
                        -w /workspace \
                        -e BASE_URL=http://host.docker.internal:8004 \
                        -e BACKEND_HEALTH_URL=http://host.docker.internal:8003/health \
                        -e CHROME_BINARY=/usr/bin/google-chrome \
                        -e CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
                        ${TEST_IMAGE} \
                        python -m pytest test_suite.py --junitxml=reports/junit.xml
                '''
            }
        }

        stage('Publish Test Results') {
            steps {
                junit allowEmptyResults: true, testResults: 'selenium_tests/reports/junit.xml'
            }
        }

    } // end stages

    post {
        always {
            script {
                // ── Set safe.directory so git commands work in Jenkins workspace ──
                sh "git config --global --add safe.directory '${env.WORKSPACE}' || true"

                // ── Determine recipient email ──────────────────────────────────
                def committer = ""
                try {
                    committer = sh(
                        script: "git log -1 --pretty=format:%ae 2>/dev/null || true",
                        returnStdout: true
                    ).trim()
                } catch (Exception e) {
                    echo "WARNING: Could not read committer email — ${e.message}"
                }

                // Fall back to env var or hard-coded address rather than crashing.
                if (!committer) {
                    committer = env.FALLBACK_EMAIL ?: "devops@example.com"
                    echo "Using fallback recipient: ${committer}"
                }

                // ── Parse surefire XML reports ─────────────────────────────────
                def reportFiles = findFiles(glob: 'selenium_tests/reports/junit.xml')
                def total   = 0
                def passed  = 0
                def failed  = 0
                def skipped = 0
                def rows    = []

                reportFiles.each { file ->
                    try {
                        def xmlText = readFile(file.path)
                        def xml     = new XmlSlurper().parseText(xmlText)

                        xml.depthFirst().findAll { node -> node.name() == 'testcase' }.each { testcase ->
                            total++
                            def name      = testcase.@name.text()      ?: 'Unknown'
                            def classname = testcase.@classname.text() ?: ''
                            def status    = 'PASSED'

                            if (testcase.failure.size() > 0 || testcase.error.size() > 0) {
                                failed++
                                status = 'FAILED'
                            } else if (testcase.skipped.size() > 0) {
                                skipped++
                                status = 'SKIPPED'
                            } else {
                                passed++
                            }

                            rows << [
                                name:      name,
                                classname: classname,
                                status:    status,
                                file:      file.name
                            ]
                        }
                    } catch (Exception parseEx) {
                        echo "WARNING: Could not parse ${file.path} — ${parseEx.message}"
                    }
                }

                // ── Build HTML report ──────────────────────────────────────────
                def statusColor = (failed > 0) ? '#b91c1c' : '#15803d'

                def rowsHtml = rows.collect { row ->
                    def color = row.status == 'FAILED'  ? '#b91c1c'
                              : row.status == 'SKIPPED' ? '#a16207'
                              :                           '#15803d'
                    """<tr>
                        <td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;">${row.name}</td>
                        <td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;">${row.classname}</td>
                        <td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;color:${color};font-weight:bold;">${row.status}</td>
                        <td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;">${row.file}</td>
                    </tr>"""
                }.join('\n')

                if (!rowsHtml) {
                    rowsHtml = '<tr><td colspan="4" style="padding:12px;color:#6b7280;">No JUnit XML results were found — the test run may have failed before tests executed.</td></tr>'
                }

                def emailBody = """
<html>
<body style="font-family:Arial,Helvetica,sans-serif;background:#f8fafc;color:#111827;line-height:1.6;">
<div style="max-width:900px;margin:0 auto;padding:24px;">
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:28px;">

  <h2 style="margin:0 0 8px;color:#0f172a;">Compulysis — Selenium Test Report</h2>
  <p style="margin:0 0 20px;color:#475569;">
    Build <strong>#${env.BUILD_NUMBER}</strong> &nbsp;|&nbsp;
    Status: <strong style="color:${statusColor};">${currentBuild.currentResult}</strong>
  </p>

  <table style="width:100%;border-collapse:collapse;margin-bottom:24px;font-size:14px;">
    <tr><td style="padding:9px 12px;background:#f1f5f9;font-weight:bold;width:40%;">Total</td>   <td style="padding:9px 12px;">${total}</td></tr>
    <tr><td style="padding:9px 12px;background:#f1f5f9;font-weight:bold;">Passed</td>  <td style="padding:9px 12px;color:#15803d;font-weight:bold;">${passed}</td></tr>
    <tr><td style="padding:9px 12px;background:#f1f5f9;font-weight:bold;">Failed</td>  <td style="padding:9px 12px;color:#b91c1c;font-weight:bold;">${failed}</td></tr>
    <tr><td style="padding:9px 12px;background:#f1f5f9;font-weight:bold;">Skipped</td> <td style="padding:9px 12px;color:#a16207;font-weight:bold;">${skipped}</td></tr>
  </table>

  <h3 style="margin:0 0 12px;color:#0f172a;">Individual Results</h3>
  <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;font-size:13px;">
    <thead>
      <tr style="background:#0f172a;color:#fff;">
        <th style="text-align:left;padding:9px 12px;">Test Name</th>
        <th style="text-align:left;padding:9px 12px;">Class</th>
        <th style="text-align:left;padding:9px 12px;">Status</th>
        <th style="text-align:left;padding:9px 12px;">Report File</th>
      </tr>
    </thead>
    <tbody>
      ${rowsHtml}
    </tbody>
  </table>

  <p style="margin:20px 0 0;font-size:12px;color:#94a3b8;">
        Jenkins URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br/>
        Python + Chrome + ChromeDriver + Selenium
  </p>

</div>
</div>
</body>
</html>
""".stripIndent().trim()

                // ── Send email ─────────────────────────────────────────────────
                try {
                    emailext(
                        to:       committer,
                        subject:  "Compulysis Build #${env.BUILD_NUMBER} — ${currentBuild.currentResult}",
                        mimeType: 'text/html',
                        body:     emailBody
                    )
                    echo "Test report email sent to: ${committer}"
                } catch (Exception mailEx) {
                    echo "WARNING: Failed to send email — ${mailEx.message}"
                    echo "Check that the Email Extension plugin is installed and SMTP is configured in Jenkins."
                }

            } // end script
        } // end always

        // ── Clean up: stop compose services ───────────────────────────────────
        cleanup {
            // sh 'docker compose down --remove-orphans || true'
            // Image is cached from Docker Hub, no need to remove it
            // sh "docker rmi ${env.TEST_IMAGE} || true"
        }

    } // end post

} // end pipeline