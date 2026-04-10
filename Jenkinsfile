pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'rm -rf compulysis-webapp'
                sh 'git clone https://github.com/zaibjahan200/compulysis-webapp'
                dir('compulysis-webapp') {
                    sh 'docker compose down --remove-orphans'
                    sh 'docker compose up -d'
                }
            }
        }
    }
}
