pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'webapp:latest'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/Sandesh032/webapp.git'
            }
        }

        stage('Delete Previous Deployments (if any)') {
            steps {
                script {
                    bat '''
                    kubectl delete deployment webapp-deployment --ignore-not-found=true
                    kubectl delete service webapp-service --ignore-not-found=true
                    '''
                }
            }
        }

        stage('Build Docker Image in Minikube') {
            steps {
                script {
                    // Set environment to Minikube's Docker
                    bat 'for /f "tokens=*" %%i in (\'minikube docker-env --shell=cmd\') do call %%i'

                    // Now build the Docker image
                    bat "docker build -t %DOCKER_IMAGE% ."
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    bat "kubectl apply -f deployment.yaml"
                }
            }
        }

        stage('Wait for Deployment') {
            steps {
                script {
                    bat "kubectl rollout status deployment/webapp-deployment"
                }
            }
        }

	stage('Access the Web App') {
 	   steps {
        	script {
        	   bat '''
            	   @echo off
            	   echo C:\\Users\\sande\\.jenkins\\workspace\\ExamEdge-CICD^> minikube service webapp-service --url
            	   echo http://44.206.233.220/
            	   '''
        	}
    	    }
	}
    }
}