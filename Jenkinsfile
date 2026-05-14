pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m unittest test_app.py'
            }
        }

        stage('Build & Push :latest') {
            steps {
                script {
                    def image = docker.build(DOCKER_REPO + ":latest")
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push "$DOCKER_REPO:latest"
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Image :latest pushed successfully. Check pod logs for startup issues."
        }
        failure {
            echo "❌ Pipeline failed. Check test logs or Docker build."
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
    }
}
