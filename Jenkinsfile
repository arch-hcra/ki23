pipeline {
    agent any

    environment {
        DOCKER_REPO = "docker.io/archcra/ki23-app"
        MANIFEST_PATH = "ki23-k8s-manifests/deployment.yaml"
    }

    stages {
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
                            docker push $DOCKER_REPO:latest
                        '''
                    }
                }
            }
        }

        stage('Update Manifest') {
            steps {
                script {
                    sh "sed -i 's|^ *image: .*|image: ${DOCKER_REPO}:latest|' ${MANIFEST_PATH}"
                    sh "git add ${MANIFEST_PATH}"
                    sh "git commit -m 'chore: update image to latest [ci skip]'"
                    sh "git remote set-url origin https://${GIT_USER}:${GIT_PASS}@github.com/arch-hcra/ki23.git"
                    sh "git push origin main"
                }
            }
        }
    }

    post {
        success { echo "✅ Image :latest pushed & manifest updated. ArgoCD will sync." }
        failure { echo "❌ Pipeline failed. Check logs for image push or Git commit errors." }
    }
}
