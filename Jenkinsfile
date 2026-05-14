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
                    def newImage = "${DOCKER_REPO}:${IMAGE_TAG}"
                    def manifestPath = "ki23-k8s-manifests/deployment.yaml"


                    def fileExists = sh(script: "test -f ${manifestPath} && echo 'exists' || echo 'missing'", returnStatus: true)
                    if (fileExists != 0) {
                        error "Файл манифеста не найден: ${manifestPath}"
                    }

            
                    def currentImageLine = sh(script: "grep 'image:' ${manifestPath}", returnStdout: true).trim()
                    if (currentImageLine.isEmpty()) {
                        error "Не найдена строка 'image:' в ${manifestPath}. Проверьте формат манифеста."
                    }

                    echo " Обновление image в ${manifestPath} на: ${newImage}"


                    sh "sed -i 's|image: .*|image: ${newImage}|' ${manifestPath}"


                    def diffOutput = sh(script: "git diff --quiet ${manifestPath} || echo 'changed'", returnStdout: true).trim()

                    if (diffOutput == "changed") {
                        echo " Изменения обнаружены в ${manifestPath}"

                        sh "git config --global user.email 'admin@example.com'"
                        sh "git config --global user.name 'Jenkins CI'"


                        sh "git add ${manifestPath}"
                        sh "git commit -m \"chore: update image to ${newImage} [ci skip]\""

                
                        sh "git push origin ${env.GIT_BRANCH}"

                        echo " Успешно обновлён и запушены манифесты: ${newImage}"
                    } else {
                        echo " Нет изменений в ${manifestPath} — пропускаем коммит."
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
