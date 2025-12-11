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

    stage('Build Docker image') {
      steps {
        script {
          sh """
            echo 'Building Docker image: ${FULL_NAME_IMAGE}'
            docker build -t ${FULL_NAME_IMAGE} .
          """
        }
      }
    }

    stage('Run container & smoke test') {
      steps {
        script {
          // Use gmail creds for container env if your app needs them to not crash on startup
          withCredentials([usernamePassword(credentialsId: 'gmail-creds', usernameVariable: 'GMAIL_USER', passwordVariable: 'GMAIL_PASS')]) {
            sh '''
              # Run container in background with Gmail ENV injected (so app won't crash if it requires env)
              cid=$(docker run -d -p 5000:5000 -e GMAIL_USER="$GMAIL_USER" -e GMAIL_PASSWORD="$GMAIL_PASS" ${IMAGE_NAME}:${IMAGE_TAG})
              echo "Container id: $cid"
              # Wait for app to be up (poll up to ~30s)
              attempts=0
              until curl --silent --fail http://localhost:5000/health || [ $attempts -ge 15 ]; do
                sleep 2
                attempts=$((attempts+1))
                echo "Waiting for app to start... $attempts"
              done
              # Show container logs for debug
              docker logs $cid || true
              # Stop and remove container
              docker rm -f $cid || true
            '''
          }
        }
      }
    }

    stage('Push to Docker Hub (optional)') {
      when {
        expression {
          // Check presence of dockerhub credentials - always try, fails gracefully if not set
          return true
        }
      }
      steps {
        script {
          // Use DockerHub creds to login, tag and push
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
            sh '''
              echo "Logging into Docker Hub as $DH_USER"
              echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
              docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DH_USER}/${IMAGE_NAME}:${IMAGE_TAG}
              docker push ${DH_USER}/${IMAGE_NAME}:${IMAGE_TAG}
            '''
          }
        }
      }
    }
  }

  post {
    always {
      sh "docker image prune -f || true"
    }
    success {
      echo "Pipeline finished successfully (image: ${IMAGE_NAME}:${IMAGE_TAG})"
    }
    failure {
      echo "Pipeline failed - check console output"
    }
  }
}
