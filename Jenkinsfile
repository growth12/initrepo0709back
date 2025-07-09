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
        sh 'docker rm -f react-app-container || true' // 컨테이너가 없어도 에러 발생하지 않도록 || true 추가
        // 호스트의 80번 포트를 컨테이너의 8000번 포트에 연결
        sh 'docker run -d -p 80:8000 --name react-app-container react-app'
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
