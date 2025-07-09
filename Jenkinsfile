pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "react-app"
        CONTAINER_NAME = "backend-app-container"
        HOST_PORT = "53000"
        CONTAINER_PORT = "8000"
    }
    
    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "🚀 Docker 이미지 빌드를 시작합니다..."
                script {
                    // 이전 이미지 정리 (용량 절약)
                    sh "docker image prune -f || true"
                    
                    // 이미지 빌드
                    sh "docker build -t ${IMAGE_NAME} ."
                }
                echo "✅ Docker 이미지 빌드 완료: ${IMAGE_NAME}:latest"
            }
        }
        
        stage('Deploy Docker Container') {
            steps {
                echo "🚀 기존 컨테이너를 제거하고 새 컨테이너를 배포합니다..."
                script {
                    // 기존 컨테이너 정리
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    
                    // 새 컨테이너 실행 (헬스체크 추가)
                    sh """
                        docker run -d \
                        -p ${HOST_PORT}:${CONTAINER_PORT} \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        ${IMAGE_NAME}
                    """
                    
                    // 컨테이너 시작 확인 (간단한 헬스체크)
                    sh "sleep 5"
                    sh "docker ps | grep ${CONTAINER_NAME}"
                }
                echo "✅ Docker 컨테이너 배포 완료: ${CONTAINER_NAME}"
            }
        }
        
        stage('Check Running Container') {
            steps {
                echo "✅ 현재 실행 중인 Docker 컨테이너 목록:"
                sh "docker ps"
                
                // 포트 확인
                sh "netstat -tlnp | grep :${HOST_PORT} || echo 'Port ${HOST_PORT} 확인 중...'"
            }
        }
    }
    
    post {
        success {
            echo "🎉🎉🎉 전체 파이프라인이 성공적으로 완료되었습니다! 백엔드 앱이 ${HOST_PORT} 포트에서 실행 중입니다. 🎉🎉🎉"
        }
        failure {
            echo "🔴🔴🔴 파이프라인 실행 중 오류가 발생하여 배포에 실패했습니다. 로그를 확인해주세요. 🔴🔴🔴"
            script {
                // 실패 시 디버깅 정보 출력
                sh "docker logs ${CONTAINER_NAME} || true"
                sh "docker ps -a | grep ${CONTAINER_NAME} || true"
            }
        }
        always {
            // 사용하지 않는 Docker 리소스 정리
            sh "docker system prune -f --volumes || true"
        }
    }
}