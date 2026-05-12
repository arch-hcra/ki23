pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m unittest test_app.py'
            }
        }

        stage('Success Notification') {
            steps {
                echo ' Tests passed! Build successful.'
            }
        }
    }

    post {
        success {
            echo ' Build succeeded! '
        }
        failure {
            echo ' Tests failed! Check the logs.'
        }
    }
}
