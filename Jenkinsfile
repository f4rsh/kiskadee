pipeline {
	agent any

	stages {
		stage('Build') {
			steps {
				sh 'virtualenv -p /usr/bin/python3 .'
				sh 'source bin/activate'
				sh 'pip install -e .'
      }
    }
		stage('Test') {
				steps {
					sh 'python setup.py test'
				}
		}
	}
}
