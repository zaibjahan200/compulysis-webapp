pipeline {
    agent any
    
    stages {
        stage('build') {
            steps {
                sh 'rm -rf compulysis-webapp'
                sh 'git clone https://github.com/zaibjahan200/compulysis-webapp'
                dir('compulysis-webapp') {
                    // Using -p ensures Jenkins creates a separate stack from your local dev\
                    //work
                    sh 'docker compose -p docker-production down --remove-orphans'
                    sh 'docker compose -p docker-production up -d --build'
                }
            }
        }
    }

    // post {
    //     success {
    //         mail to: 'j44551076@gmail.com',
    //              subject: 'Jenkins Build Success: compulysis-webapp',
    //              body: "The Jenkins pipeline completed successfully.\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
    //     }
    //     failure {
    //         mail to: 'j44551076@gmail.com',
    //              subject: 'Jenkins Build Failure: compulysis-webapp',
    //              body: "The Jenkins pipeline failed.\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
    //     }
    // }
}
