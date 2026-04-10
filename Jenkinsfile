pipeline {
    agent any
    
    stages {
        stage('build') {
            steps {
                // Jenkins already checks out the repo in the workspace.
                sh 'docker compose down --remove-orphans --volumes || true'
                sh 'docker compose up -d --build --remove-orphans'
            }
        }
    }

    post {
        success {
            mail to: 'j44551076@gmail.com',
                 subject: 'Jenkins Build Success: compulysis-webapp',
                 body: "The Jenkins pipeline completed successfully.\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
        }
        failure {
            mail to: 'j44551076@gmail.com',
                 subject: 'Jenkins Build Failure: compulysis-webapp',
                 body: "The Jenkins pipeline failed.\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
        }
    }
}
