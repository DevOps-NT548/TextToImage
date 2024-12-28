pipeline {
    agent any

    options {
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment {
        registry = 'liuchangming/txt2img'
        registryCredential = 'Docker-Access-Token'
        envCredential = 'env-variables'
        keyCredential = 'namsee_key'
    }

    stages {
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
                    def backendImage = docker.build("${registry}_backend:$BUILD_NUMBER", 
                                                    "-f ${backendDockerfile} .")
                    
                    echo 'Building frontend image for deployment..'
                    def frontendDockerfile = 'deployment/model_predictor/Frontend_Dockerfile'
                    def frontendImage = docker.build("${registry}_frontend:$BUILD_NUMBER", 
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
        stage('Deploy application to Google Kubernetes Engine') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // name of the container to be used for helm upgrade
                        image 'liuchangming/jenkins:lts' // the image containing helm
                        alwaysPullImage true // Always pull image in case of using the same tag
                    }
                }
            }
            environment {
                CREDENTIAL_JSON_FILE_NAME = '/tmp/namsee_key.json'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'env-variables', variable: 'ENV_VARIABLES'),
                    file(credentialsId: 'namsee_key', variable: 'JSON_KEY_PATH')
                ]) {
                    script {
                        echo 'Deploying application to GKE..'
                        container('helm') {
                            echo 'Setting up environment variables..'

                            // Save the .env variables to a file
                            sh '''
                            echo "$ENV_VARIABLES" > /tmp/.env
                            '''

                            // Copy the JSON key file to the deployment environment
                            sh '''
                            cp $JSON_KEY_PATH ${CREDENTIAL_JSON_FILE_NAME}
                            '''

                            // Deploy with Helm
                            echo 'Deploying the new images to GKE..'
                            sh '''
                            helm upgrade --install txt2img ./helm/txt2img --namespace model-serving \
                            --set-file envFile=/tmp/.env \
                            --set-file credentialJsonFile=${CREDENTIAL_JSON_FILE_NAME}
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
