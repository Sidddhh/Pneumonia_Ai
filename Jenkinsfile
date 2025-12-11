pipeline {
    agent any

    environment {
        IMAGE_NAME = "pneumonia_ai"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        FULL_NAME_IMAGE = "${IMAGE_NAME}:${IMAGE_TAG}"
    }

    options {
        timestamps()
        skipStagesAfterUnstable()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat """
                echo Building Docker image: %FULL_NAME_IMAGE%
                docker build -t %FULL_NAME_IMAGE% .
                """
            }
        }

        stage('Run container & smoke test') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'gmail-creds',
                                                  usernameVariable: 'GMAIL_USER',
                                                  passwordVariable: 'GMAIL_PASS')]) {

                    bat """
                    echo Starting container...
                    docker run -d -p 5000:5000 --name pneumonia_test ^
                      -e GMAIL_USER="%GMAIL_USER%" ^
                      -e GMAIL_PASSWORD="%GMAIL_PASS%" ^
                      %FULL_NAME_IMAGE%

                    echo Checking health endpoint...

                    powershell -Command ^
                      "for (\$i=0; \$i -lt 20; \$i++) { ^
                          try { ^
                              Invoke-WebRequest -Uri 'http://localhost:5000/health' -UseBasicParsing -TimeoutSec 5; ^
                              Write-Host 'Health OK'; exit 0; ^
                          } catch { ^
                              Start-Sleep -Seconds 2 ^
                          } ^
                      }; exit 1"

                    docker logs pneumonia_test
                    docker stop pneumonia_test
                    docker rm pneumonia_test
                    """
                }
            }
        }

        stage('Push to Docker Hub (optional)') {
            when {
                expression { return true }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {

                    bat """
                    echo Logging into DockerHub...
                    echo %DH_PASS% | docker login -u %DH_USER% --password-stdin
                    docker tag %FULL_NAME_IMAGE% %DH_USER%/%IMAGE_NAME%:%IMAGE_TAG%
                    docker push %DH_USER%/%IMAGE_NAME%:%IMAGE_TAG%
                    """
                }
            }
        }
    }

    post {
        always {
            bat "docker image prune -f"
        }
        success {
            echo "Pipeline finished successfully — image: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline FAILED — check logs"
        }
    }
}
