pipeline {
    agent any

    // environment {
    //     CREDENTIAL_JSON_FILE_NAME = credentials('CREDENTIAL_JSON_FILE_NAME')
    //     STORAGE_BUCKET_NAME = credentials('STORAGE_BUCKET_NAME')
    //     SECRET_KEY = credentials('SECRET_KEY')
    //     DATABASE_NAME = credentials('DATABASE_NAME')
    //     DATABASE_USER = credentials('DATABASE_USER')
    //     DATABASE_PASSWORD = credentials('DATABASE_PASSWORD')
    //     DATABASE_HOST = credentials('DATABASE_HOST')
    //     DATABASE_PORT = credentials('DATABASE_PORT')
    // }

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment{
        registry = 'liuchangming/txt2img'
        registryCredential = 'Dockerhub-Access-Token'      
    }

    stages {
        // stage('Test') {
        //     agent {
        //         docker {
        //             image 'python:3.9' 
        //         }
        //     }
        //     steps {
        //         echo 'Testing model correctness..'
        //         sh 'pip install -r requirements.txt && pytest'
        //     }
        // }
        stage('Build') {
            steps {
                script {
                    echo 'Building backend image for deployment..'
                    // def backendDockerfile = 'deployment/model_predictor/Backend_Dockerfile'
                    // def backendImage = docker.build("${registry}_backend:$BUILD_NUMBER", 
                    //                                 "-f ${backendDockerfile} .")
                    
                    echo 'Building frontend image for deployment..'
                    // def frontendDockerfile = 'deployment/model_predictor/Frontend_Dockerfile'
                    // def frontendImage = docker.build("${registry}_frontend:$BUILD_NUMBER", 
                    //                                  "-f ${frontendDockerfile} .")
                    
                    echo 'Pushing backend image to dockerhub..'
                    // docker.withRegistry('', registryCredential) {
                    //     backendImage.push()
                    //     backendImage.push('latest')
                    // }
                    
                    echo 'Pushing frontend image to dockerhub..'
                    // docker.withRegistry('', registryCredential) {
                    //     frontendImage.push()
                    //     frontendImage.push('latest')
                    // }
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
                    // container('helm') {
                    //     sh """
                    //     helm upgrade --install txt2img ./helm/txt2img --namespace model-serving \
                    //     --set CREDENTIAL_JSON_FILE_NAME=${env.CREDENTIAL_JSON_FILE_NAME} \
                    //     --set STORAGE_BUCKET_NAME=${env.STORAGE_BUCKET_NAME} \
                    //     --set SECRET_KEY=${env.SECRET_KEY} \
                    //     --set DATABASE_NAME=${env.DATABASE_NAME} \
                    //     --set DATABASE_USER=${env.DATABASE_USER} \
                    //     --set DATABASE_PASSWORD=${env.DATABASE_PASSWORD} \
                    //     --set DATABASE_HOST=${env.DATABASE_HOST} \
                    //     --set DATABASE_PORT=${env.DATABASE_PORT}
                    //     """
                    // }
                    // echo 'Running update_backend_ip_on_k8s.sh script..'
                    // sh """
                    // cd scripts
                    // chmod +x update_backend_ip_on_k8s.sh
                    // ./update_backend_ip_on_k8s.sh
                    // """
                }
            }
        }
    }
}