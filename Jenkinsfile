pipeline {
    agent any

    environment {
        PROJECT_PATH = '/Sites/home_service_classification'
        DATABASE_DRIVER = 'ODBC Driver 18 for SQL Server'
        DATABASE_SERVER = 'localhost'
        DATABASE_NAME = 'home-service-chatbot'
        DATABASE_CREDENTIALS = credentials('DATABASE_CREDENTIALS')
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

    stages {
        stage('Setup Virtual Environment') {
            steps {
                dir("${PROJECT_PATH}") {
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
        }

        stage('Install Dependencies') {
            steps {
                dir("${PROJECT_PATH}") {
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
        }

        // stage('Run Tests') {
        //     steps {
        //         dir("${PROJECT_PATH}") {
        //             script {
        //                 sh 'source .venv/bin/activate && pytest tests/'
        //             }
        //         }
        //     }
        // }

        stage('Preprocess Data') {
            steps {
                dir("${PROJECT_PATH}") {
                    script {
                        sh 'source .venv/bin/activate && python scripts/data_preprocessing.py'
                    }
                }
            }
        }

        stage('Retrain Model') {
            steps {
                dir("${PROJECT_PATH}") {
                    script {
                        sh 'source .venv/bin/activate && python train_model.py'
                    }
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
            when {
                expression { return currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                dir("${PROJECT_PATH}") {
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
