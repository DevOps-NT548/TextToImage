pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }

    environment {
        registry = 'liuchangming/txt2img'
        registryCredential = 'Docker-Access-Token'
        envCredential = 'env-variables'
        keyCredential = 'namsee_key'
        sonarProjectKey = 'your-sonarqube-project-key'
        sonarHostUrl = 'http://localhost:9000'
        sonarLogin = 'your-sonarqube-token'
    }

    stages {
        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('SonarQube') {
                        sh 'sonar-scanner -Dsonar.projectKey=$sonarProjectKey -Dsonar.sources=. -Dsonar.host.url=$sonarHostUrl -Dsonar.login=$sonarLogin'
                    }
                }
            }
        }

        stage('Test') {
            parallel {
                stage('Backend Tests') {
                    agent {
                        docker {
                            image 'python:3.11'
                        }
                    }
                    steps {
                        echo 'Testing backend..'
                        withCredentials([
                            string(credentialsId: envCredential, variable: 'ENV_VARS'),
                            file(credentialsId: keyCredential, variable: 'JSON_KEY_PATH')
                        ]) {
                            sh '''
                            # Write the .env file
                            echo "$ENV_VARS" > .env
                            echo "CREDENTIAL_JSON_FILE_NAME=$JSON_KEY_PATH" >> .env
                            export $(cat .env | xargs)

                            # Run the backend tests
                            cd Backend
                            pip install -r requirements.txt
                            python manage.py test
                            '''
                        }
                    }
                }
                stage('Frontend Tests') {
                    agent {
                        docker {
                            image 'node:16'
                        }
                    }
                    steps {
                        echo 'Testing frontend..'
                        sh '''
                        cd Frontend
                        npm install
                        npm run lint
                        npm run build
                        '''
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building backend image for deployment..'
                    def backendDockerfile = 'deployment/model_predictor/Backend_Dockerfile'
                    def backendImage = docker.build("${registry}_backend:latest", 
                                                    "-f ${backendDockerfile} .")
                    
                    echo 'Building frontend image for deployment..'
                    def frontendDockerfile = 'deployment/model_predictor/Frontend_Dockerfile'
                    def frontendImage = docker.build("${registry}_frontend:latest", 
                                                     "-f ${frontendDockerfile} .")
                    
                    echo 'Pushing backend image to dockerhub..'
                    docker.withRegistry('', registryCredential) {
                        backendImage.push()
                        backendImage.push('latest')
                    }
                    
                    echo 'Pushing frontend image to dockerhub..'
                    docker.withRegistry('', registryCredential) {
                        frontendImage.push()
                        frontendImage.push('latest')
                    }
                }
            }
        }

        stage('Trivy Scan') {
            steps {
                script {
                    sh 'trivy image ${registry}_backend:latest'
                    sh 'trivy image ${registry}_frontend:latest'
                }
            }
        }

        stage('Deploy application to Google Kubernetes Engine') {
            agent {
                kubernetes {
                    yaml '''
apiVersion: v1
kind: Pod
metadata:
  namespace: model-serving
spec:
  serviceAccountName: jenkins-sa
  containers:
  - name: helm
    image: dtzar/helm-kubectl:3.11.1
    command:
    - cat
    tty: true
'''
                }
            }
            steps {
                withCredentials([
                    string(credentialsId: envCredential, variable: 'ENV_VARIABLES'),
                    file(credentialsId: keyCredential, variable: 'JSON_KEY_PATH')
                ]) {
                    script {
                        echo 'Deploying application to GKE..'
                        container('helm') {
                            echo 'Setting up environment variables and deploying the application..'
                            sh '''
                            echo "$ENV_VARIABLES" > .env
                            echo "CREDENTIAL_JSON_FILE_NAME=$JSON_KEY_PATH" >> .env
                            export $(cat .env | xargs)

                            helm upgrade --install txt2img ./helm/txt2img --namespace model-serving \
                            --set STORAGE_BUCKET_NAME="$STORAGE_BUCKET_NAME" \
                            --set SECRET_KEY="$SECRET_KEY" \
                            --set DATABASE_ENGINE="$DATABASE_ENGINE" \
                            --set DATABASE_NAME="$DATABASE_NAME" \
                            --set DATABASE_USER="$DATABASE_USER" \
                            --set DATABASE_PASSWORD="$DATABASE_PASSWORD" \
                            --set DATABASE_HOST="$DATABASE_HOST" \
                            --set DATABASE_PORT="$DATABASE_PORT"
                            '''

                            echo 'Running update_backend_ip_on_k8s.sh script..'
                            sh '''
                            cd scripts
                            chmod +x update_backend_ip_on_k8s.sh
                            ./update_backend_ip_on_k8s.sh
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
            sh '''
                docker container prune -f
                docker image prune -af
                docker volume prune -f
                docker network prune -f
                docker system prune -f
            '''
        }
    }
}