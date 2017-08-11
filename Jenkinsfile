pipeline {
  agent any

  environment {
  	USER = "jenkins"
  }

  stages {
    stage('change-repo-owner') {
      steps {
        sh 'chown -R ${USER}.${USER} .'
      }
    }
    stage('Build') {
      steps {
        sh 'sudo -H -u ${USER} virtualenv -p /usr/bin/python3 .'
	sh 'sudo -H -u ${USER} source bin/activate && sudo -H -u ${USER}  pip install -e .'
      }
    }
    stage('build-docker-images') {
      steps {
        sh '(sudo -H -u ${USER} cd util/dockerfiles/cppcheck && sudo -H -u ${USER} docker build . -t cppcheck)'
        sh '(sudo -H -u ${USER} cd util/dockerfiles/flawfinder && sudo -H -u ${USER} docker build . -t flawfinder)'
      }
    }
    stage('Test') {
      steps {
        sh "source bin/activate && python kiskadee_coverage.py"
      }

    post {
        success {
          // publish html
          publishHTML target: [
              allowMissing: false,
              alwaysLinkToLastBuild: false,
              keepAll: true,
              reportDir: 'covhtml',
              reportFiles: 'index.html',
              reportName: 'coverage report'
            ]
        }
      }
    }
  }
}
