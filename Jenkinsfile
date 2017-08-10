pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'virtualenv -p /usr/bin/python3 .'
	sh 'source bin/activate && pip install -e .'
      }
    }
    stage('build-docker-images') {
      steps {
        sh '(cd util/dockerfiles/cppcheck && docker build . -t cppcheck)'
        sh '(cd util/dockerfiles/flawfinder && docker build . -t flawfinder)'
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
