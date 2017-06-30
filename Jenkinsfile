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
        sh 'docker build . --file util/dockerfiles/cppcheck/Dockerfile -t cppcheck '
        sh 'docker build . --file util/dockerfiles/flawfinder/Dockerfile -t flawfinder '
      }
    }
    stage('Test') {
      steps {
        sh 'source bin/activate && python setup.py test'
      }
    }
  }
}
