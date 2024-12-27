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
        GCP_CREDENTIALS = credentials('namsee_key_credentials')
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
                    // Write credentials to temp files
                    writeFile file: 'namsee_key.json', text: GCP_CREDENTIALS
                    writeFile file: '.env', text: ENV_FILE

                    // Build images with secrets
                    def backendDockerfile = 'deployment/model_predictor/Backend_Dockerfile'
                    def backendImage = docker.build("${registry}_backend:$BUILD_NUMBER",
                                                "--secret id=namsee_key,src=namsee_key.json " +
                                                "-f ${backendDockerfile} .")
                    
                    def frontendDockerfile = 'deployment/model_predictor/Frontend_Dockerfile' 
                    def frontendImage = docker.build("${registry}_frontend:$BUILD_NUMBER",
                                                "--secret id=namsee_key,src=namsee_key.json " +
                                                "-f ${frontendDockerfile} .")

                    // Clean up sensitive files
                    sh 'rm -f namsee_key.json .env'
                    
                    // Push images
                    docker.withRegistry('', registryCredential) {
                        backendImage.push()
                        backendImage.push('latest')
                        frontendImage.push()
                        frontendImage.push('latest')
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
            cleanWs(
                cleanWhenNotBuilt: true,
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [
                    [pattern: '**/.git/**', type: 'EXCLUDE'],
                    [pattern: '**/node_modules/**', type: 'EXCLUDE']
                ]
            )
            
            sh '''
                docker container prune -f
                docker image prune -af
                docker volume prune -f
                docker network prune -f
            '''
        }
    }
}