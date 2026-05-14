pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        MANIFEST_PATH = "ki23-k8s-manifests/kustomization.yaml"  // ← ВАЖНО: теперь kustomization.yaml, а не deployment.yaml!
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
                    def imageWithTag = "${DOCKER_REPO}:${gitCommitShort}"

                    def image = docker.build(imageWithTag)

                    withCredentials([usernamePassword(
                        credentialsId: 'docker-token',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push "$IMAGE_TAG"
                        '''
                    }


                    env.IMAGE_TAG = gitCommitShort
                }
            }
        }

        stage('Update Kustomize Manifest in Git') {
            steps {
                script {
                    def manifest = "${MANIFEST_PATH}"
                    def newImage = "${DOCKER_REPO}:${env.IMAGE_TAG}"


                    sh "git checkout ${GIT_BRANCH}"
                    sh "git fetch origin"
                    sh "git reset --hard origin/${GIT_BRANCH}"


                    def kustomizeContent = readFile(manifest)
                    if (!kustomizeContent.contains("newTag:")) {
                        error "kustomization.yaml не содержит 'newTag:' — убедитесь, что он настроен для замены тега"
                    }

                    
                    sh "sed -i 's|newTag: .*|newTag: ${env.IMAGE_TAG}|' ${manifest}"

              
                    def diff = sh(script: "git diff --cached ${manifest} || true", returnStdout: true).trim()

                    if (diff != "") {
                        echo "✅ Изменён тег в ${manifest}: ${env.IMAGE_TAG}"

                   
                        sh 'git config --global user.email "jenkins@ci.example.com"'
                        sh 'git config --global user.name "Jenkins CI"'

                   
                        sh "git add ${manifest}"
                        sh "git commit -m \"chore: update image tag to ${env.IMAGE_TAG}\""

                        withCredentials([string(
                            credentialsId: 'new_jenk_ci/cd',
                            variable: 'GITHUB_TOKEN'
                        )]) {
                            sh "git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/arch-hcra/ki23.git"
                            sh "git push origin ${GIT_BRANCH}"
                        }

                        echo "✅ Успешно обновлён и запушены манифесты в Git: ${newImage}"
                    } else {
                        echo "ℹ️ Нет изменений в ${manifest}, пропускаем коммит."
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Сборка, пуш и обновление манифеста прошли успешно. ArgoCD автоматически синхронизирует изменения."
        }
        failure {
            echo "❌ Ошибка: проверьте логи сборки. Убедитесь, что тесты прошли, образ запушен, и манифест обновлён."
        }
    }
}
