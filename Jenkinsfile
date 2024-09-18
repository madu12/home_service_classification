pipeline {
    agent any

    environment {
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
                        if [ ! -d ".venv" ]; then
                            echo "Creating virtual environment..."
                            python3 -m venv .venv
                        fi

                        # Activate the virtual environment
                        source .venv/bin/activate

                        # Install required dependencies
                        echo "Installing dependencies..."
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Preprocess Data') {
            steps {
                script {
                    echo "Running data preprocessing..."
                    sh 'source .venv/bin/activate && python scripts/data_preprocessing.py'
                }
            }
        }

        stage('Retrain Model') {
            steps {
                script {
                    echo "Retraining the model..."
                    sh 'source .venv/bin/activate && python train_model.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '**/models/*.pkl', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/models/*.csv', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/models/*.npy', allowEmptyArchive: true
                    archiveArtifacts artifacts: '**/logs/*.log', allowEmptyArchive: true
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
