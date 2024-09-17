pipeline {
    agent any

    environment {
        // Use Jenkins credentials to set environment variables
        DATABASE_DRIVER = 'ODBC Driver 18 for SQL Server'
        DATABASE_SERVER = 'localhost'
        DATABASE_NAME = 'home-service-chatbot'
        DATABASE_CREDENTIALS = credentials('DATABASE_CREDENTIALS')
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        # Activate the virtual environment
                        source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate

                        # Install required dependencies
                        echo "Installing dependencies..."
                        pip3 install -r requirements.txt
                    '''
                }
            }
        }

        stage('Preprocess Data') {
            steps {
                script {
                    echo "Running data preprocessing..."
                    sh 'python3 scripts/data_preprocessing.py'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running tests..."
                    sh './test.sh'
                }
            }
        }

        stage('Retrain Model') {
            steps {
                script {
                    echo "Retraining the model..."
                    sh './retrain.sh'
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
            cleanWs()  // Clean the workspace after the job completes
        }
    }
}
