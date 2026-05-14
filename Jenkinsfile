pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        MANIFEST_PATH = "ki23-k8s-manifests/deployment.yaml"
        GIT_BRANCH = "main"
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
                def gitCommitShort = "${env.GIT_COMMIT}".take(8)
                def IMAGE_FULL = "${DOCKER_REPO}:${gitCommitShort}"
                env.IMAGE_TAG = gitCommitShort
                env.IMAGE_FULL = IMAGE_FULL

                echo " Собираем образ: ${IMAGE_FULL}"

                def image = docker.build(IMAGE_FULL)
                sh "docker images '${IMAGE_FULL}'"

                withCredentials([usernamePassword(
                  credentialsId: 'docker-token',
                  usernameVariable: 'DOCKER_USER',
                  passwordVariable: 'DOCKER_PASS'
                )]) {
                  sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    docker push "$IMAGE_FULL"
                '''
            }

            echo " Успешно запущен образ: ${IMAGE_FULL}"
        }
    }
}

        stage('Update Manifest in Git') {
            steps {
                script {
                    def manifest = "${MANIFEST_PATH}"
                    def newImage = "${DOCKER_REPO}:${env.IMAGE_TAG}"


                    sh "git checkout ${GIT_BRANCH}"
                    sh "git fetch origin"
                    sh "git reset --hard origin/${GIT_BRANCH}"


                    sh "sed -i \"s|image: ${DOCKER_REPO}:.*|image: ${newImage}|g\" ${manifest}"


                    def diff = sh(script: "git diff --cached ${manifest} || true", returnStdout: true).trim()

                    if (diff != "") {
                        echo " Изменён образ в ${manifest}: ${newImage}"

                        
                        sh 'git config --global user.email "jenkins@ci.example.com"'
                        sh 'git config --global user.name "Jenkins CI"'

                        
                        sh "git add ${manifest}"
                        sh "git commit -m \"chore: update image to ${env.IMAGE_TAG}\""

                        withCredentials([string(
                            credentialsId: 'new_jenk_ci/cd',
                            variable: 'GITHUB_TOKEN'
                        )]) {
                            sh "git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/arch-hcra/ki23.git"
                            sh "git push origin ${GIT_BRANCH}"
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
            echo " Ошибка: проверьте логи сборки. Убедитесь, что тесты прошли, образ запушено, и манифест обновлён."
        }
    }
}
