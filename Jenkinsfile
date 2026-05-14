pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        IMAGE_TAG = "${env.GIT_COMMIT.take(8)}"
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
                    withCredentials([usernamePassword(credentialsId: 'docker-token', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
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


                    sh "git checkout main"
                    sh "git fetch origin"
                    sh "git reset --hard origin/main"


                    sh "sed -i 's/^[[:space:]]*image:[[:space:]]*.*/image: ${newImage}/' ${MANIFEST_PATH}"


                    def changes = sh(script: "git diff --quiet ${manifest} || echo 'changed'", returnStdout: true).trim()

                    if (changes == "changed") {
                        echo " Change ${manifest}: ${newImage}"

  
                        sh 'git config --global user.email "admin@example.com"'
                        sh 'git config --global user.name "Jenkins CI"'

                        sh "git add ${manifest}"
                        sh "git commit -m \"chore: update image to ${IMAGE_TAG}\""

                        withCredentials([string(credentialsId: 'new_jenk_ci/cd', variable: 'GITHUB_TOKEN')]) {
                            sh "git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/arch-hcra/ki23.git"
                            sh "git push origin main"
                        }

                        echo " Успешно обновлён и запушены манифесты в Git: ${newImage}"
                    } else {
                        echo " Нет изменений в ${manifest}, пропускаем коммит."
                    }
                }
            }
        }
    }

    post {
        success {
            echo " Сборка, пуш и обновление манифеста прошли успешно. ArgoCD автоматически синхронизирует изменения."
        }
        failure {
            echo " Ошибка: проверьте логи сборки и убедитесь, что тесты прошли и образ запушено."
        }
    }
}
