pipeline {
    agent any
    
    stages {
        stage('build') {
            steps {
                // Jenkins already checks out the repo in the workspace.
                sh 'docker compose down --remove-orphans || true'
                sh 'docker compose pull'
                sh 'docker compose up -d --remove-orphans'
            }
        }
    }

}
