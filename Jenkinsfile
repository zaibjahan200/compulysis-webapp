pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'docker compose down --remove-orphans || true'
                sh 'docker compose pull || true'
                sh 'docker compose up -d --remove-orphans'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -e

                    for target in http://localhost:8003/health http://localhost:8004; do
                        echo "Waiting for ${target}"
                        ready=false

                        for attempt in $(seq 1 30); do
                            if curl -fsS "${target}" >/dev/null; then
                                ready=true
                                break
                            fi
                            sleep 5
                        done

                        if [ "${ready}" != "true" ]; then
                            echo "Timed out waiting for ${target}"
                            exit 1
                        fi
                    done

                    docker run --rm \
                        --add-host=host.docker.internal:host-gateway \
                        -v "$WORKSPACE/tests:/workspace" \
                        -w /workspace \
                        markhobson/maven-chrome:latest \
                        mvn clean test \
                          -DbaseUrl=http://host.docker.internal:8004 \
                          -DbackendHealthUrl=http://host.docker.internal:8003/health \
                          --batch-mode --no-transfer-progress
                '''
            }
        }
    }

    post {
        always {
            script {
                sh "git config --global --add safe.directory ${env.WORKSPACE} || true"

                def committer = sh(
                    script: "git log -1 --pretty=format:%ae",
                    returnStdout: true
                ).trim()

                if (!committer) {
                    error('Unable to determine committer email for test report delivery.')
                }

                def reportFiles = findFiles(glob: 'tests/target/surefire-reports/*.xml')
                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0
                def rows = []

                reportFiles.each { file ->
                    def xmlText = readFile(file.path)
                    def xml = new XmlSlurper().parseText(xmlText)

                    xml.testcase.each { testcase ->
                        total++

                        def name = testcase.@name.text() ?: 'Unknown test'
                        def classname = testcase.@classname.text()
                        def status = 'PASSED'
                        def symbol = 'PASSED'

                        if (testcase.failure.size() > 0 || testcase.error.size() > 0) {
                            failed++
                            status = 'FAILED'
                            symbol = 'FAILED'
                        } else if (testcase.skipped.size() > 0) {
                            skipped++
                            status = 'SKIPPED'
                            symbol = 'SKIPPED'
                        } else {
                            passed++
                        }

                        rows << [
                            name: name,
                            classname: classname,
                            status: status,
                            symbol: symbol,
                            file: file.name
                        ]
                    }
                }

                def rowsHtml = rows.collect { row ->
                    """
                    <tr>
                        <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">${row.symbol}: ${row.name}</td>
                        <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">${row.classname}</td>
                        <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">${row.status}</td>
                        <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">${row.file}</td>
                    </tr>
                    """.stripIndent().trim()
                }.join('\n')

                def emailBody = """
                    <html>
                        <body style="font-family:Arial,Helvetica,sans-serif;background:#f8fafc;color:#111827;line-height:1.5;">
                            <div style="max-width:860px;margin:0 auto;padding:24px;">
                                <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;">
                                    <h2 style="margin:0 0 12px;color:#0f172a;">Selenium Test Execution Report</h2>

                                    <p>
                                        Build <strong>#${env.BUILD_NUMBER}</strong> finished with status
                                        <strong>${currentBuild.currentResult}</strong>.
                                    </p>

                                    <table style="width:100%;border-collapse:collapse;margin:0 0 20px;">
                                        <tr>
                                            <td style="padding:10px 12px;background:#f1f5f9;font-weight:bold;">Total Tests</td>
                                            <td style="padding:10px 12px;background:#f8fafc;">${total}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px 12px;background:#f1f5f9;font-weight:bold;">Passed</td>
                                            <td style="padding:10px 12px;background:#f8fafc;color:#15803d;">${passed}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px 12px;background:#f1f5f9;font-weight:bold;">Failed</td>
                                            <td style="padding:10px 12px;background:#f8fafc;color:#b91c1c;">${failed}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px 12px;background:#f1f5f9;font-weight:bold;">Skipped</td>
                                            <td style="padding:10px 12px;background:#f8fafc;color:#a16207;">${skipped}</td>
                                        </tr>
                                    </table>

                                    <h3>Detailed Results</h3>

                                    <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;">
                                        <thead>
                                            <tr style="background:#0f172a;color:#ffffff;">
                                                <th style="text-align:left;padding:10px 12px;">Test</th>
                                                <th style="text-align:left;padding:10px 12px;">Class</th>
                                                <th style="text-align:left;padding:10px 12px;">Status</th>
                                                <th style="text-align:left;padding:10px 12px;">Report File</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${rowsHtml ?: '<tr><td colspan="4" style="padding:12px;">No JUnit results were found.</td></tr>'}
                                        </tbody>
                                    </table>

                                    <p style="margin:20px 0 0;color:#475569;">
                                        Jenkins Build URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br/>
                                        Executed inside Docker using the Maven + Chrome image.
                                    </p>
                                </div>
                            </div>
                        </body>
                    </html>
                """.stripIndent().trim()

                emailext(
                    to: committer,
                    subject: "Selenium Build #${env.BUILD_NUMBER} - ${currentBuild.currentResult}",
                    mimeType: 'text/html',
                    body: emailBody
                )
            }
        }
    }
}