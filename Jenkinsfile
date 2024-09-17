pipeline {
    agent any

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Load environment variables from the .env file
                    sh '''
                        export $(grep -v '^#' .env | xargs)
                        ./build.sh
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        export $(grep -v '^#' .env | xargs)
                        ./test.sh
                    '''
                }
            }
        }

        stage('Retrain Model') {
            steps {
                script {
                    sh '''
                        export $(grep -v '^#' .env | xargs)
                        ./retrain.sh
                    '''
                }
            }
        }

        stage('Deploy Model') {
            steps {
                script {
                    echo "Deployment handled in retrain script."
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}
