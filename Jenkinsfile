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

}
