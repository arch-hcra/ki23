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

            
                    sh "git checkout -- ${manifestPath}"

            
                    def currentImageLine = sh(script: "grep '^ *image:' ${manifestPath}", returnStdout: true).trim()
                    if (currentImageLine.isEmpty()) {
                        error "Не найдена строка 'image:' в ${manifestPath}. Проверьте формат манифеста."
                    }
                    echo "Текущий image: ${currentImageLine}"

                    def oldImage = currentImageLine.split(':')[1].trim()
                    echo "Обновление image с '${oldImage}' на '${newImage}'"

            
                    sh "sed -i 's|^ *image: .*|image: ${newImage}|' ${manifestPath}"

            
                    def newImageLine = sh(script: "grep '^ *image:' ${manifestPath}", returnStdout: true).trim()
                    if (newImageLine != "image: ${newImage}") {
                        error "Ошибка: sed не применил изменения. Ожидается: 'image: ${newImage}', получено: '${newImageLine}'"
                    }
                    echo " Успешно обновлено: ${newImageLine}"

            
                    def diffOutput = sh(script: "git diff --quiet ${manifestPath} || echo 'changed'", returnStatus: true)

                    if (diffOutput == 0) {
                        echo " Нет изменений в ${manifestPath} — возможно, файл уже актуален."
                    } else {
                    echo " Изменения обнаружены в ${manifestPath}"

                
                    sh "git config --global user.email 'jenkins@ci.example.com'"
                    sh "git config --global user.name 'Jenkins CI'"

                    sh "git add ${manifestPath}"
                    sh "git commit -m \"chore: update image to ${newImage} [ci skip]\""

                    def branch = env.GIT_BRANCH ?: 'main'

                    withCredentials([usernamePassword(
                        credentialsId: 'arch-hcra',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_PASS'
                    )]) {
                        sh "git remote set-url origin https://${GIT_USER}:${GIT_PASS}@github.com/arch-hcra/ki23.git"
                        sh "git push origin ${branch}"
                    }

                    echo "✅ Успешно обновлён и запушены манифесты: ${newImage}"
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
