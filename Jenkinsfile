pipeline {
    agent any

    environment {
        IMAGE_NAME = 'smart-recipe-finder'
        IMAGE_TAG  = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                // Use standard shell commands instead of the docker DSL plugin
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Test') {
            steps {
                // Run a temporary container to execute tests
                sh "docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} python -m pytest tests/ --tb=short -v"
            }
        }

        stage('Deploy') {
            steps {
                // Stop and remove old container if it exists, then start new one
                sh """
                    docker stop ${IMAGE_NAME} || true
                    docker rm ${IMAGE_NAME} || true
                    docker run -d --name ${IMAGE_NAME} \
                        -p 5000:5000 \
                        --env-file .env \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
    }
}
