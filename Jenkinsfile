pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'acoolstick/examedge-nginx:latest'
        EC2_PUBLIC_IP = 'ec2-3-83-160-24.compute-1.amazonaws.com'  
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/Utsav-J/examedge-nginx.git'
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

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Overwrite deployment.yaml with updated image
                    writeFile file: 'deployment.yaml', text: """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: ${DOCKER_IMAGE}
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  type: LoadBalancer
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
"""
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
                    bat """
                    @echo off
                    echo Application should be accessible at:
                    echo http://%EC2_PUBLIC_IP%:30080/
                    """
                }
            }
        }
    }
}
