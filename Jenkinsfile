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
                        cp "${WORKSPACE}/models/final_classifier.pkl" "${PROJECT_PATH}/models/" || echo "No final_classifier.pkl file to copy"
                        cp "${WORKSPACE}/models/final_word2vec_model.pkl" "${PROJECT_PATH}/models/" || echo "No final_word2vec_model.pkl file to copy"
                        cp "${WORKSPACE}/models/tfidf_vectorizer.pkl" "${PROJECT_PATH}/models/" || echo "No tfidf_vectorizer.pkl file to copy"
                        cp "${WORKSPACE}/models/vectorized_descriptions_combined.pkl" "${PROJECT_PATH}/models/" || echo "No vectorized_descriptions_combined.pkl file to copy"
                        cp "${WORKSPACE}/models/descriptions_combined.csv" "${PROJECT_PATH}/models/" || echo "No descriptions_combined.csv file to copy"
                        cp "${WORKSPACE}/models/combined_feature_dims.npy" "${PROJECT_PATH}/models/" || echo "No combined_feature_dims.npy file to copy"
                        cp "${WORKSPACE}/models/vectorized_descriptions_combined.npy" "${PROJECT_PATH}/models/" || echo "No vectorized_descriptions_combined.npy file to copy"
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
