pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Install Dependencies in Venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -m unittest test_app.py
                '''
            }
        }

        stage('Build & Push Git Commit Tag') {
            steps {
                script {
                    def image = docker.build("${DOCKER_REPO}:${env.GIT_COMMIT_SHORT}")
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push "$DOCKER_REPO:$GIT_COMMIT_SHORT"
                        '''
                    }
                    
                }
            }
        }
    }

    post {
        success {
            echo "✅ Image ${DOCKER_REPO}:${env.GIT_COMMIT_SHORT} pushed successfully."

            sh '''
                git config --global user.email "jenkins@localhost"
                git config --global user.name "Jenkins"
                git checkout main
                sed -i "s|image: docker.io/archcra/ki23-app:.*|image: docker.io/archcra/ki23-app:${env.GIT_COMMIT_SHORT}|g" ki23-k8s-manifests/deployment.yaml
                git add ki23-k8s-manifests/deployment.yaml
                git commit -m "chore: update image tag to ${env.GIT_COMMIT_SHORT}"
                git push origin main
            '''
        }
        failure {
            echo "❌ Pipeline failed. Check test logs or Docker build."
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
    }
}
