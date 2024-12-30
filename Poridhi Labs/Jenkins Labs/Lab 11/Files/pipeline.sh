pipeline {
    agent any
    tools {
        jdk 'JDK-17'
        nodejs 'NODE-18'
    }
    environment {
        DOCKER_IMAGE = 'konami98/simple-react'
    }
    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Docker System Cleanup') {
            steps {
                sh '''
                    docker system prune -af --volumes || true
                    if docker images ${DOCKER_IMAGE} -q | grep -q .; then
                        docker rmi $(docker images ${DOCKER_IMAGE} -q) || true
                    fi
                '''
            }
        }
        stage('Checkout from Git') {
            steps {
                git branch: 'main', url: 'https://github.com/Konami33/Simple-React.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                dir('frontend') {
                    sh """
                        npm cache clean --force
                        rm -rf node_modules package-lock.json
                        npm install
                    """
                }
            }
        }
        stage('Docker Build & Push') {
            steps {
                script {
                    try {
                        def imageTag = "${BUILD_NUMBER}"
                        def fullImageName = "${DOCKER_IMAGE}:${imageTag}"
                        
                        dir('frontend') {
                            withDockerRegistry(credentialsId: 'Dockerhub', toolName: 'Docker') {
                                sh """
                                    docker build --no-cache -t ${fullImageName} . || (echo 'Docker build failed' && exit 1)
                                    docker push ${fullImageName} || (echo 'Docker push failed' && exit 1)
                                """
                            }
                        }
                    } catch (Exception e) {
                        echo "Docker build or push failed: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }
        stage('Update ConfigMap') {
            steps {
                script {
                    try {
                        def imageTag = "${BUILD_NUMBER}"
                        withKubeConfig([credentialsId: 'kubernetes']) {
                            sh """
                                kubectl create configmap image-tag-config \
                                    --from-literal=IMAGE_TAG=${imageTag} \
                                    --dry-run=client -o yaml | \
                                kubectl apply -f - || (echo 'ConfigMap update failed' && exit 1)
                            """
                        }
                    } catch (Exception e) {
                        echo "ConfigMap update failed: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    try {
                        def imageTag = "${BUILD_NUMBER}"
                        withKubeConfig([credentialsId: 'kubernetes']) {
                            sh """
                                # Verify kubectl connection
                                kubectl get nodes || (echo 'Kubernetes cluster connection failed' && exit 1)
                                
                                # Replace image tag in deployment file
                                sed -i 's|${DOCKER_IMAGE}:[^\"]*|${DOCKER_IMAGE}:${imageTag}|' kubernetes/deployment.yaml
                                
                                # Apply the manifests with error checking
                                kubectl apply -f kubernetes/deployment.yaml || (echo 'Deployment apply failed' && exit 1)
                                kubectl apply -f kubernetes/service.yaml || (echo 'Service apply failed' && exit 1)
                                
                                # Wait for deployment with timeout
                                timeout 300s kubectl rollout status deployment/simple-react || (echo 'Deployment rollout failed' && exit 1)
                                
                                # Verify deployment
                                kubectl get pods | grep simple-react
                            """
                        }
                    } catch (Exception e) {
                        echo "Kubernetes deployment failed: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline execution completed."
            sh 'docker system prune -af --volumes || true'
        }
        success {
            echo "Deployment successful!"
            echo "Access the application at NodePort 30000"
        }
        failure {
            echo "Deployment failed. Please check the logs."
            script {
                try {
                    withKubeConfig([credentialsId: 'kubernetes']) {
                        sh """
                            echo 'Kubernetes Deployment Status:'
                            kubectl get deployments
                            echo 'Pod Status:'
                            kubectl get pods
                            echo 'Recent Pod Logs:'
                            kubectl logs -l app=simple-react --tail=50 || true
                        """
                    }
                } catch (Exception e) {
                    echo "Failed to fetch debug information: ${e.getMessage()}"
                }
            }
        }
    }
}