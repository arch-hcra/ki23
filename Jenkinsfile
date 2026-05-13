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
                    def manifest = "${MANIFEST_PATH}"
                    def newImage = "${DOCKER_REPO}:${IMAGE_TAG}"

            
                    sh "sed -i \"s|image: .*|image: ${newImage}|g\" ${manifest}"


                    def changes = sh(script: "git diff --quiet ${manifest} || echo 'changed'", returnStdout: true).trim()

                    if (changes == "changed") {

                        sh 'git config --global user.email "jenkins@example.com"'
                        sh 'git config --global user.name "Jenkins"'

                        sh 'git checkout main || git checkout -b main'

                        sh "git add ${manifest}"
                        sh "git commit -m \"chore: update image to ${IMAGE_TAG}\""

                
                        withCredentials([string(credentialsId: 'new_jenk_ci/cd', variable: 'GITHUB_TOKEN')]) {
                            sh """
                                set -e
                                git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/arch-hcra/ki23-k8s-manifests.git
                                git remote -v
                                git push origin main
                            """
                        }
                } else {
                    echo "No changes in ${manifest}, skipping commit."
                }
            }
        }
    }

    }

    post {
        success {
            echo ' Build, push and Git update succeeded! ArgoCD will auto-sync.'
        }
        failure {
            echo ' Tests failed or deployment failed! Check logs.'
        }
    }
}
