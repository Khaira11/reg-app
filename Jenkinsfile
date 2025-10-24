pipeline {
    agent any

    environment {
        IMAGE_NAME = 'khaira23/flask-jenkins:latest'
        DEPLOYMENT_NAME = 'flask-deployment'
        NAMESPACE = 'default'
    }

    stages {

        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image'
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Login & Push to DockerHub') {
            steps {
                echo '🔐 Logging in to DockerHub'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh '''
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker push $IMAGE_NAME
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo '☸️ Deploying application to Kubernetes...'
                withKubeConfig([credentialsId: 'k8s-credential']) {
                    sh '''
                        # Apply Deployment and Service files
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml

                        # Optional: Wait for rollout to complete
                        kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo '🔍 Checking application status'
                withKubeConfig([credentialsId: 'k8s-credentials']) {
                    sh '''
                        kubectl get pods -n $NAMESPACE
                        kubectl get svc -n $NAMESPACE
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '🎉 Pipeline execution completed'
        }
    }
}

