pipeline {
  agent any

  stages {

    stage('Create Virtualenv') {
      steps {
        sh 'virtualenv -p /usr/bin/python3 .'
	      sh 'source bin/activate && pip install -e .'
	      sh "source bin/activate && pip install fedmsg[consumers]"
	      sh "source bin/activate && pip install -r test_requirements.txt"
      }
    }

    stage('Build Docker Images') {
      steps {
        sh 'source bin/activate && make analyzers'
      }
    }

    stage('Run Tests') {
      steps {
        sh "source bin/activate && make test"
      }
	post {
		success {
		// publish html
		publishHTML target: [
		allowMissing: false,
		alwaysLinkToLastBuild: false,
		keepAll: true,
		reportDir: 'htmlcov',
		reportFiles: 'index.html',
		reportName: 'coverage report'
		]
		}
	}
    }

    /* stage('Deploy') {
	steps {
	  sh "if [ '${env.BRANCH_NAME}' = 'master' ] \
	  || [ '${env.BRANCH_NAME}' = 'continuos_dep' ]; then \
	  source bin/activate && make deploy INVENTORY=production; \
	  fi"
	}
    } */
 }
}
