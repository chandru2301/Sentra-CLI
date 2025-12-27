pipeline {
  agent any
  
  environment {
    AI_ESCALATOR_ENABLED = "true"
    AI_ESCALATOR_MODEL = "mistralai/devstral-2-2512:free"
    AI_ESCALATOR_TIMEOUT = "5"
    OPENROUTER_API_KEY = credentials('openrouter-key')
  }
  
  stages {
    stage('Sentra') {
      steps {
        sh '''
          pip install sentra
          sentra scan --base ${CHANGE_TARGET:-main}
        '''
      }
    }
  }
  
  post {
    failure {
      echo "Sentra blocked this change. Check the scan output above."
    }
  }
}

