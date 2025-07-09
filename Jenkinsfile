pipeline {
    agent any

    environment {
        IMAGE_NAME = "react-app"
        CONTAINER_NAME = "react-app-container"
        PORT = "80"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $IMAGE_NAME ."
            }
        }

        stage('Deploy') {
    steps {
        sh 'docker rm -f backend-app-container || true' // 컨테이너 이름은 'backend-app-container'로 가정
        // 호스트의 53000번 포트를 컨테이너의 8000번 포트에 연결
        sh 'docker run -d -p 53000:8000 --name backend-app-container backend-app'
    }
}

        stage('Check Running Container') {
            steps {
                echo "✅ 현재 실행 중인 컨테이너 목록:"
                sh "docker ps"
            }
        }
    }

    post {
        success {
            echo "✅ 배포 성공!"
        }
        failure {
            echo "❌ 배포 실패!"
        }
    }
}
