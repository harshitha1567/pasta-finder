pipeline {
    agent any

    environment {
        IMAGE_NAME = 'smart-recipe-finder'
        IMAGE_TAG  = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh "docker build -t %IMAGE_NAME%:%IMAGE_TAG% ."
            }
        }

        stage('Test') {
            steps {
                sh "docker run --rm %IMAGE_NAME%:%IMAGE_TAG% python -m pytest tests/ --tb=short -v"
            }
        }

        stage('Deploy') {
            steps {
                sh """
                    docker stop %IMAGE_NAME% || exit 0
                    docker rm %IMAGE_NAME% || exit 0
                    docker run -d --name %IMAGE_NAME% -p 5000:5000 --env-file .env %IMAGE_NAME%:%IMAGE_TAG%
                """
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
