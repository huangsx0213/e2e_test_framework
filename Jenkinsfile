pipeline {
    agent any

    parameters {
        choice(name: 'TEST_TYPE', choices: ['e2e', 'api', 'web'], description: 'Type of test to run')
        string(name: 'ACTIVE_ENVIRONMENT', defaultValue: 'SIT', description: 'Active environment for testing')
        string(name: 'TEST_CASES_PATH', defaultValue: 'test_cases/e2e_test_cases.xlsx', description: 'Path to test cases file')
        booleanParam(name: 'CLEAR_SAVED_FIELDS', defaultValue: true, description: 'Clear saved fields after test')
        string(name: 'TC_ID_LIST', defaultValue: '', description: 'Comma-separated list of Test Case IDs to run')
        string(name: 'TAGS', defaultValue: '', description: 'Comma-separated list of tags to filter test cases')
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        python3 --version
                        pip3 --version
                        pip3 install -r requirements.txt
                    '''
                }
            }
        }

        stage('Update Configuration') {
            steps {
                script {
                    def configFile = "configs/${params.TEST_TYPE}_test_config.yaml"
                    sh """
                        . venv/bin/activate
                        python3 yaml_config_cli.py ${configFile} --update active_environment ${params.ACTIVE_ENVIRONMENT} --update test_cases_path ${params.TEST_CASES_PATH} --update clear_saved_fields_after_test ${params.CLEAR_SAVED_FIELDS}
                    """
                    if (params.TC_ID_LIST) {
                        def tcIdList = params.TC_ID_LIST.split(',')
                        tcIdList.each { tcId ->
                            sh ". venv/bin/activate && python3 yaml_config_cli.py ${configFile} --add-to-list tc_id_list ${tcId.trim()}"
                        }
                    }
                    if (params.TAGS) {
                        def tagsList = params.TAGS.split(',')
                        tagsList.each { tag ->
                            sh ". venv/bin/activate && python3 yaml_config_cli.py ${configFile} --add-to-list tags ${tag.trim()}"
                        }
                    }
                }
            }
        }

        stage('Start Flask Server') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        cd testing_server
                        nohup python3 server.py > flask.log 2>&1 &
                        echo $! > flask.pid
                        sleep 1 # wait for server to start
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def testCommand = "python main.py --${params.TEST_TYPE}"
                    sh ". venv/bin/activate && ${testCommand}"
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report/**/*', allowEmptyArchive: true
            robot outputPath: 'report', logFileName: 'log.html', outputFileName: 'output.xml', reportFileName: 'report.html', passThreshold: 100, unstableThreshold: 75
            script {
                sh '''
                    if [ -f flask.pid ]; then
                        PID=$(cat flask.pid)
                        if ps -p $PID > /dev/null 2>&1; then
                            echo "Stopping Flask server (PID: $PID)"
                            kill $PID || true
                        else
                            echo "Flask server (PID: $PID) is not running"
                        fi
                        rm flask.pid
                    else
                        echo "flask.pid file not found"
                    fi
                '''
            }
            publishHTML(target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'report',
            reportFiles: 'dashboard.html',
            reportName: 'Robot Framework Dashboard'
            ])

        }
    }
}