pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "khaira23/flask-jenkins"
        K8S_NAMESPACE = "default"
    }
    
    stages {
        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image'
                sh 'docker build -t ${DOCKER_IMAGE}:latest .'
            }
        }
        
        stage('Login & Push to DockerHub') {
            steps {
                echo '🔐 Logging in to DockerHub'
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        
        stage('Test K8s Connection') {
            steps {
                script {
                    configFileProvider([configFile(fileId: 'k8s-config', variable: 'KUBECONFIG')]) {
                        sh '''
                            echo "Testing Kubernetes connection..."
                            kubectl --kubeconfig=$KUBECONFIG cluster-info
                            kubectl --kubeconfig=$KUBECONFIG get nodes
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    configFileProvider([configFile(fileId: 'k8s-config', variable: 'KUBECONFIG')]) {
                        sh '''
                            echo "Deploying to Kubernetes..."
                            kubectl --kubeconfig=$KUBECONFIG apply -f k8s/ --validate=false
                            sleep 15
                            kubectl --kubeconfig=$KUBECONFIG get all -l app=flask-app
                        '''
                    }
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    configFileProvider([configFile(fileId: 'k8s-config', variable: 'KUBECONFIG')]) {
                        sh '''
                            echo "Verifying deployment..."
                            kubectl --kubeconfig=$KUBECONFIG rollout status deployment/flask-app --timeout=300s
                            kubectl --kubeconfig=$KUBECONFIG get services
                        '''
                    }
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
