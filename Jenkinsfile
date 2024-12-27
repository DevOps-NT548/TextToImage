pipeline {
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment{
        registry = 'liuchangming/txt2img'
        registryCredential = 'Dockerhub-Access-Token'      
        //GCP_CREDENTIALS = credentials('gcp-service-account')
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
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            echo 'Testing backend..'
                            sh '''
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
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
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
        }
        stage('Build') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'gcp-service-account', variable: 'GCP_CREDENTIALS_FILE')]) {
                        sh "cp \$GCP_CREDENTIALS_FILE namsee_key.json"
                        // Build images using Makefile
                        sh 'make build_app_image'
                        // Push images using Makefile
                        sh 'make register_app_image'
                        // Clean up sensitive files
                        sh 'rm -f namsee_key.json'
                    }
                }
            }
        }
        stage('Deploy application to Google Kubernestes Engine') {
            agent{
                kubernetes{
                    containerTemplate{
                        name 'helm' // name of the container to be used for helm upgrade
                        image 'liuchangming/jenkins:lts' // the image containing helm
                        alwaysPullImage true // Always pull image in case of using the same tag
                     }
                }
            }
            steps{
                script{
                    echo 'Deploying application to GKE..'
                    container('helm') {
                        echo 'Deploying the new images to GKE..'
                        sh '''
                        helm upgrade --install txt2img ./helm/txt2img --namespace model-serving
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

    post {
        always {
            cleanWs()
            sh '''
                docker container prune -f
                docker image prune -af
                docker volume prune -f
                docker network prune -f
            '''
        }
    }
}