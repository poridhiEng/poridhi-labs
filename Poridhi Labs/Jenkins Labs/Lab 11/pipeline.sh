pipeline {
    agent any
    tools {
        jdk 'JDK-17'
        nodejs 'NODE-18'
    }
    environment {
        DOCKER_IMAGE = 'konami98/simple-react'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
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
                    sh "npm install"
                }
            }
        }
        stage('Docker Build & Push') {
            steps {
                script {
                    def imageTag = "${BUILD_NUMBER}"
                    def fullImageName = "${DOCKER_IMAGE}:${imageTag}"
                    
                    dir('frontend') {
                        withDockerRegistry(credentialsId: 'Dockerhub', toolName: 'Docker') {
                            sh "docker build -t ${fullImageName} ."
                            sh "docker push ${fullImageName}"
                        }
                    }
                }
            }
        }
        stage('Update ConfigMap') {
            steps {
                script {
                    def imageTag = "${BUILD_NUMBER}"
                    
                    sh """
                    kubectl create configmap image-tag-config --from-literal=IMAGE_TAG=${imageTag} --dry-run=client -o yaml | kubectl apply -f -
                    """
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    kubernetesDeploy(
                        kubeconfigId: 'kubernetes',
                        configs: 'kubernetes/deployment.yaml'
                    )
                    kubernetesDeploy(
                        kubeconfigId: 'kubernetes',
                        configs: 'kubernetes/service.yaml'
                    )
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline execution completed."
        }
        success {
            echo "Deployment successful!"
        }
        failure {
            echo "Deployment failed. Please check the logs."
        }
    }
}
