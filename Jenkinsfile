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
        sh '(cd util/dockerfiles/cppcheck &&  docker build . -t cppcheck)'
        sh '(cd util/dockerfiles/flawfinder && docker build . -t flawfinder)'
      }
    }
    stage('Test') {
      steps {
        sh "chmod u+x run_tests_and_coverage.sh"
        sh "source bin/activate && ./run_tests_and_coverage.sh"
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
  }
}
