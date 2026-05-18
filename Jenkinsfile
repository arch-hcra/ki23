pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        KUSTOMIZATION_PATH = "ki23-k8s-manifests/kustomization.yaml"
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

        stage('Run Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    python3 -m unittest test_app.py
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
 
                    sh "docker build -t ${DOCKER_REPO}:${env.GIT_COMMIT_SHORT} ."


                    withCredentials([usernamePassword(
                        credentialsId: 'docker-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {

                        sh """
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push "${DOCKER_REPO}:${env.GIT_COMMIT_SHORT}"
                        """
                    }
                }
            }
        }

        stage('Update Kustomization') {
            steps {
                script {

                    sh """
                        sed -i "s|newTag: .*|newTag: ${env.GIT_COMMIT_SHORT}|g" ${KUSTOMIZATION_PATH}
                        cat ${KUSTOMIZATION_PATH}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Image ${DOCKER_REPO}:${env.GIT_COMMIT_SHORT} pushed successfully."
            sh """
                git config --global user.email "jenkins@localhost"
                git config --global user.name "Jenkins"
                git add ${KUSTOMIZATION_PATH}
                git commit -m "chore: update image tag to ${env.GIT_COMMIT_SHORT}"
                git push origin main
            """
        }
        failure {
            echo "❌ Pipeline failed. Check logs."
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
    }
}