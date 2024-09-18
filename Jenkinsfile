pipeline {
    agent any

    environment {
        PROJECT_PATH = '/Users/madhushan/Sites/home_service_classification'
        DATABASE_DRIVER = 'ODBC Driver 18 for SQL Server'
        DATABASE_SERVER = 'localhost'
        DATABASE_NAME = 'home-service-chatbot'
        DATABASE_CREDENTIALS = credentials('DATABASE_CREDENTIALS')
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {
        stage('Setup Virtual Environment') {
            steps {
                script {
                    sh '''
                        if [ ! -d ".venv" ]; then
                            echo "Creating virtual environment..."
                            python3 -m venv .venv
                        fi
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        source .venv/bin/activate
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

        stage('Move Models to Project Folder') {
            steps {
                script {
                    sh '''
                        echo "Creating target directory if it does not exist..."
                        mkdir -p ${PROJECT_PATH}/models

                        echo "Moving models to the project folder..."
                        mv ${WORKSPACE}/models/*.pkl ${PROJECT_PATH}/models/ || echo "No .pkl files to move"
                        mv ${WORKSPACE}/models/*.csv ${PROJECT_PATH}/models/ || echo "No .csv files to move"
                        mv ${WORKSPACE}/models/*.npy ${PROJECT_PATH}/models/ || echo "No .npy files to move"
                    '''
                }
            }
        }

        stage('Deploy Model') {
            when {
                expression { return currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                dir(env.PROJECT_PATH) {
                    script {
                        echo "Deployment handled in retrain script."
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed!'
        }
        always {
            cleanWs()
        }
    }
}
