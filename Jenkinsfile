pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        IMAGE_TAG   = "${env.GIT_COMMIT.take(8)}"
        MANIFEST_PATH = "ki23-k8s-manifests/deployment.yaml"
    }

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

        stage('Build & Push Docker Image') {
            steps {
                script {

                    def image = docker.build("${DOCKER_REPO}:${IMAGE_TAG}")
                    

                    withCredentials([usernamePassword(
                        credentialsId: 'docker-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push ${DOCKER_REPO}:${IMAGE_TAG}
                        '''
                    }
                }
            }
        }

        stage('Update Manifest in Git') {
            steps {
                script {
                    sh '''
                        sed -i "s|image: .*${DOCKER_REPO}:.*|image: ${DOCKER_REPO}:${IMAGE_TAG}|g" ${MANIFEST_PATH}
                    '''

                    sh 'git diff'


                    sh '''
                        git config --global user.email "jenkins@example.com"
                        git config --global user.name "Jenkins"
                        git add ${MANIFEST_PATH}
                        git commit -m "chore: update image to ${IMAGE_TAG}" || echo "No changes to commit"
                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build, push and Git update succeeded! ArgoCD will auto-sync.'
        }
        failure {
            echo '❌ Tests failed or deployment failed! Check logs.'
        }
    }
}
