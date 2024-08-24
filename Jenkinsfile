pipeline {
    agent any
    parameters {
        choice(name: 'TEST_TYPE', choices: ['api', 'web', 'e2e'], description: 'Type of test to run')
        string(name: 'ACTIVE_ENVIRONMENT', defaultValue: 'DEV', description: 'Active environment for testing')
        string(name: 'TEST_CASES_PATH', defaultValue: 'test_cases/api_test_cases.xlsx', description: 'Path to test cases file')
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
                    sleep 1  # 等待服务器启动
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
            junit 'report/output.xml'
            script {
                sh '''
                if [ -f flask.pid ]; then
                    kill $(cat flask.pid)
                    rm flask.pid
                fi
                '''
            }
        }
    }
}