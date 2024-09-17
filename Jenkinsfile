pipeline {
    agent any

    environment {
        // Use Jenkins credentials to set environment variables
        DATABASE_DRIVER = 'ODBC Driver 18 for SQL Server'
        DATABASE_SERVER = 'localhost'
        DATABASE_NAME = 'home-service-chatbot'
        DATABASE_CREDENTIALS = credentials('DATABASE_CREDENTIALS')  // Reference credentials by ID
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')  // Reference API key by ID
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Check if virtual environment exists and create if not
                    sh '''
                        # Check if virtual environment exists
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

        // stage('Run Tests') {
        //     steps {
        //         script {
        //             echo "Running tests..."
        //             sh '''
        //                 # Activate the virtual environment
        //                 source .venv/bin/activate
                        
        //                 # Ensure pytest is installed
        //                 pip install pytest

        //                 # Run the tests
        //                 ./test.sh
        //             '''
        //         }
        //     }
        // }

        stage('Retrain Model') {
            steps {
                script {
                    echo "Retraining the model..."
                    sh 'source .venv/bin/activate && ./retrain.sh'
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
