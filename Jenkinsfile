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
                withPythonEnv('Python3') {
                    sh 'python --version'
                    sh 'pip --version'
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Update Configuration') {
            steps {
                withPythonEnv('Python3') {
                    script {
                        def configFile = "configs/${params.TEST_TYPE}_test_config.yaml"
                        sh "python yaml_config_cli.py ${configFile} --update active_environment ${params.ACTIVE_ENVIRONMENT}"
                        sh "python yaml_config_cli.py ${configFile} --update test_cases_path ${params.TEST_CASES_PATH}"
                        sh "python yaml_config_cli.py ${configFile} --update clear_saved_fields_after_test ${params.CLEAR_SAVED_FIELDS}"

                        if (params.TC_ID_LIST) {
                            def tcIdList = params.TC_ID_LIST.split(',')
                            tcIdList.each { tcId ->
                                sh "python yaml_config_cli.py ${configFile} --add-to-list tc_id_list ${tcId.trim()}"
                            }
                        }

                        if (params.TAGS) {
                            def tagsList = params.TAGS.split(',')
                            tagsList.each { tag ->
                                sh "python yaml_config_cli.py ${configFile} --add-to-list tags ${tag.trim()}"
                            }
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                withPythonEnv('Python3') {
                    script {
                        def testCommand = "python main.py --${params.TEST_TYPE}"
                        sh "${testCommand}"
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report/**/*', allowEmptyArchive: true
            junit 'report/output.xml'
        }
    }
}