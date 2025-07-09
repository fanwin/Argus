pipeline {
    agent any
    
    parameters {
        choice(
            name: 'TEST_ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'TEST_TYPE',
            choices: ['all', 'smoke', 'api', 'web', 'regression'],
            description: '选择测试类型'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge'],
            description: '选择浏览器'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: '是否使用无头模式'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: '是否并行执行测试'
        )
        string(
            name: 'PYTEST_MARKERS',
            defaultValue: '',
            description: '自定义pytest标记 (例如: "smoke and api")'
        )
    }
    
    environment {
        // 环境变量
        TEST_ENV = "${params.TEST_ENVIRONMENT}"
        BROWSER = "${params.BROWSER}"
        HEADLESS = "${params.HEADLESS}"
        PYTHONPATH = "${WORKSPACE}"
        
        // 工具版本
        PYTHON_VERSION = "3.10"
        ALLURE_VERSION = "2.24.0"
        
        // 报告目录
        REPORTS_DIR = "${WORKSPACE}/reports"
        ALLURE_RESULTS = "${REPORTS_DIR}/allure-results"
        ALLURE_REPORT = "${REPORTS_DIR}/allure-report"
        
        // 通知配置
        SLACK_CHANNEL = "#testing"
        EMAIL_RECIPIENTS = "qa-team@yourproject.com,dev-team@yourproject.com"
    }
    
    options {
        // 构建选项
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 2, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
        
        // 并发构建控制
        disableConcurrentBuilds()
    }
    
    triggers {
        // 定时触发
        cron(env.BRANCH_NAME == 'main' ? 'H 2 * * *' : '')  // 主分支每天凌晨2点
        
        // 代码变更触发
        pollSCM('H/5 * * * *')  // 每5分钟检查一次代码变更
    }
    
    stages {
        stage('Preparation') {
            steps {
                script {
                    // 显示构建信息
                    echo "=== 构建信息 ==="
                    echo "分支: ${env.BRANCH_NAME}"
                    echo "构建号: ${env.BUILD_NUMBER}"
                    echo "测试环境: ${params.TEST_ENVIRONMENT}"
                    echo "测试类型: ${params.TEST_TYPE}"
                    echo "浏览器: ${params.BROWSER}"
                    echo "无头模式: ${params.HEADLESS}"
                    echo "并行执行: ${params.PARALLEL_EXECUTION}"
                    
                    // 设置构建描述
                    currentBuild.description = "Env: ${params.TEST_ENVIRONMENT} | Type: ${params.TEST_TYPE} | Browser: ${params.BROWSER}"
                }
                
                // 清理工作空间
                cleanWs()
                
                // 检出代码
                checkout scm
                
                // 创建报告目录
                sh '''
                    mkdir -p ${REPORTS_DIR}/allure-results
                    mkdir -p ${REPORTS_DIR}/screenshots
                    mkdir -p ${REPORTS_DIR}/coverage
                    mkdir -p ${REPORTS_DIR}/logs
                '''
            }
        }
        
        stage('Environment Setup') {
            parallel {
                stage('Python Environment') {
                    steps {
                        sh '''
                            # 设置Python虚拟环境
                            python${PYTHON_VERSION} -m venv venv
                            source venv/bin/activate
                            
                            # 升级pip
                            pip install --upgrade pip
                            
                            # 安装依赖
                            pip install -r requirements.txt
                            
                            # 验证安装
                            pip list > ${REPORTS_DIR}/pip-list.txt
                        '''
                    }
                }
                
                stage('Browser Setup') {
                    when {
                        expression { params.TEST_TYPE in ['all', 'web'] }
                    }
                    steps {
                        sh '''
                            # 安装浏览器驱动
                            source venv/bin/activate
                            
                            if [ "${BROWSER}" = "chrome" ]; then
                                # 安装Chrome和ChromeDriver
                                wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
                                echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
                                apt-get update
                                apt-get install -y google-chrome-stable
                            elif [ "${BROWSER}" = "firefox" ]; then
                                # 安装Firefox和GeckoDriver
                                apt-get update
                                apt-get install -y firefox
                            fi
                        '''
                    }
                }
                
                stage('Allure Setup') {
                    steps {
                        sh '''
                            # 安装Allure
                            if [ ! -d "/opt/allure-${ALLURE_VERSION}" ]; then
                                wget -O allure.tgz https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz
                                tar -xzf allure.tgz -C /opt/
                                ln -sf /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure
                            fi
                            
                            # 验证Allure安装
                            allure --version
                        '''
                    }
                }
            }
        }
        
        stage('Code Quality Check') {
            parallel {
                stage('Linting') {
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            # 代码风格检查
                            flake8 . --output-file=${REPORTS_DIR}/flake8-report.txt --exit-zero
                            
                            # 代码复杂度检查
                            radon cc . --json > ${REPORTS_DIR}/radon-report.json
                        '''
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            # 安全漏洞扫描
                            bandit -r . -f json -o ${REPORTS_DIR}/bandit-report.json --exit-zero
                            
                            # 依赖安全检查
                            safety check --json --output ${REPORTS_DIR}/safety-report.json --exit-zero
                        '''
                    }
                }
            }
        }
        
        stage('Framework Validation') {
            steps {
                sh '''
                    source venv/bin/activate
                    
                    # 验证测试框架
                    python test_framework.py > ${REPORTS_DIR}/framework-validation.log 2>&1
                '''
            }
        }
        
        stage('Test Execution') {
            parallel {
                stage('Smoke Tests') {
                    when {
                        expression { params.TEST_TYPE in ['all', 'smoke'] }
                    }
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            pytest -m smoke \\
                                --alluredir=${ALLURE_RESULTS} \\
                                --html=${REPORTS_DIR}/smoke-report.html \\
                                --self-contained-html \\
                                --junitxml=${REPORTS_DIR}/smoke-junit.xml \\
                                --cov=. --cov-report=xml:${REPORTS_DIR}/smoke-coverage.xml \\
                                -v --tb=short
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'smoke-report.html',
                                reportName: 'Smoke Test Report'
                            ])
                        }
                    }
                }
                
                stage('API Tests') {
                    when {
                        expression { params.TEST_TYPE in ['all', 'api'] }
                    }
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            PYTEST_ARGS="-m api"
                            if [ "${params.PARALLEL_EXECUTION}" = "true" ]; then
                                PYTEST_ARGS="${PYTEST_ARGS} -n auto"
                            fi
                            
                            pytest ${PYTEST_ARGS} \\
                                --alluredir=${ALLURE_RESULTS} \\
                                --html=${REPORTS_DIR}/api-report.html \\
                                --self-contained-html \\
                                --junitxml=${REPORTS_DIR}/api-junit.xml \\
                                --cov=. --cov-report=xml:${REPORTS_DIR}/api-coverage.xml \\
                                -v --tb=short
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'api-report.html',
                                reportName: 'API Test Report'
                            ])
                        }
                    }
                }
                
                stage('Web UI Tests') {
                    when {
                        expression { params.TEST_TYPE in ['all', 'web'] }
                    }
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            PYTEST_ARGS="-m web"
                            if [ "${params.PARALLEL_EXECUTION}" = "true" ]; then
                                PYTEST_ARGS="${PYTEST_ARGS} -n auto"
                            fi
                            
                            pytest ${PYTEST_ARGS} \\
                                --alluredir=${ALLURE_RESULTS} \\
                                --html=${REPORTS_DIR}/web-report.html \\
                                --self-contained-html \\
                                --junitxml=${REPORTS_DIR}/web-junit.xml \\
                                --cov=. --cov-report=xml:${REPORTS_DIR}/web-coverage.xml \\
                                -v --tb=short
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'web-report.html',
                                reportName: 'Web UI Test Report'
                            ])
                        }
                    }
                }
                
                stage('Regression Tests') {
                    when {
                        expression { params.TEST_TYPE in ['all', 'regression'] }
                    }
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            PYTEST_ARGS="-m regression"
                            if [ "${params.PARALLEL_EXECUTION}" = "true" ]; then
                                PYTEST_ARGS="${PYTEST_ARGS} -n auto"
                            fi
                            
                            pytest ${PYTEST_ARGS} \\
                                --alluredir=${ALLURE_RESULTS} \\
                                --html=${REPORTS_DIR}/regression-report.html \\
                                --self-contained-html \\
                                --junitxml=${REPORTS_DIR}/regression-junit.xml \\
                                --cov=. --cov-report=xml:${REPORTS_DIR}/regression-coverage.xml \\
                                -v --tb=short
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'regression-report.html',
                                reportName: 'Regression Test Report'
                            ])
                        }
                    }
                }
                
                stage('Custom Tests') {
                    when {
                        expression { params.PYTEST_MARKERS != '' }
                    }
                    steps {
                        sh '''
                            source venv/bin/activate
                            
                            PYTEST_ARGS="-m \\"${params.PYTEST_MARKERS}\\""
                            if [ "${params.PARALLEL_EXECUTION}" = "true" ]; then
                                PYTEST_ARGS="${PYTEST_ARGS} -n auto"
                            fi
                            
                            pytest ${PYTEST_ARGS} \\
                                --alluredir=${ALLURE_RESULTS} \\
                                --html=${REPORTS_DIR}/custom-report.html \\
                                --self-contained-html \\
                                --junitxml=${REPORTS_DIR}/custom-junit.xml \\
                                --cov=. --cov-report=xml:${REPORTS_DIR}/custom-coverage.xml \\
                                -v --tb=short
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'custom-report.html',
                                reportName: 'Custom Test Report'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Report Generation') {
            steps {
                script {
                    // 生成Allure报告
                    sh '''
                        if [ -d "${ALLURE_RESULTS}" ] && [ "$(ls -A ${ALLURE_RESULTS})" ]; then
                            allure generate ${ALLURE_RESULTS} -o ${ALLURE_REPORT} --clean
                        else
                            echo "No Allure results found"
                        fi
                    '''
                    
                    // 合并覆盖率报告
                    sh '''
                        source venv/bin/activate
                        
                        if ls ${REPORTS_DIR}/*-coverage.xml 1> /dev/null 2>&1; then
                            coverage combine ${REPORTS_DIR}/*-coverage.xml
                            coverage report > ${REPORTS_DIR}/coverage-summary.txt
                            coverage html -d ${REPORTS_DIR}/coverage-html
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // 发布测试结果
            publishTestResults testResultsPattern: 'reports/*-junit.xml'
            
            // 发布Allure报告
            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'reports/allure-results']]
            ])
            
            // 发布覆盖率报告
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports/coverage-html',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
            
            // 归档构件
            archiveArtifacts artifacts: 'reports/**/*', fingerprint: true, allowEmptyArchive: true
            
            // 清理工作空间
            cleanWs()
        }
        
        success {
            script {
                // 成功通知
                def message = """
                ✅ 测试执行成功！
                
                项目: ${env.JOB_NAME}
                构建: #${env.BUILD_NUMBER}
                分支: ${env.BRANCH_NAME}
                环境: ${params.TEST_ENVIRONMENT}
                类型: ${params.TEST_TYPE}
                浏览器: ${params.BROWSER}
                
                报告链接: ${env.BUILD_URL}allure/
                """
                
                // Slack通知
                slackSend(
                    channel: env.SLACK_CHANNEL,
                    color: 'good',
                    message: message
                )
                
                // 邮件通知（仅主分支）
                if (env.BRANCH_NAME == 'main') {
                    emailext(
                        subject: "✅ 测试成功 - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: message,
                        to: env.EMAIL_RECIPIENTS
                    )
                }
            }
        }
        
        failure {
            script {
                // 失败通知
                def message = """
                ❌ 测试执行失败！
                
                项目: ${env.JOB_NAME}
                构建: #${env.BUILD_NUMBER}
                分支: ${env.BRANCH_NAME}
                环境: ${params.TEST_ENVIRONMENT}
                类型: ${params.TEST_TYPE}
                浏览器: ${params.BROWSER}
                
                详细信息: ${env.BUILD_URL}console
                报告链接: ${env.BUILD_URL}allure/
                """
                
                // Slack通知
                slackSend(
                    channel: env.SLACK_CHANNEL,
                    color: 'danger',
                    message: message
                )
                
                // 邮件通知
                emailext(
                    subject: "❌ 测试失败 - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: message,
                    to: env.EMAIL_RECIPIENTS
                )
            }
        }
        
        unstable {
            script {
                // 不稳定通知
                def message = """
                ⚠️ 测试不稳定！
                
                项目: ${env.JOB_NAME}
                构建: #${env.BUILD_NUMBER}
                分支: ${env.BRANCH_NAME}
                环境: ${params.TEST_ENVIRONMENT}
                类型: ${params.TEST_TYPE}
                浏览器: ${params.BROWSER}
                
                详细信息: ${env.BUILD_URL}console
                报告链接: ${env.BUILD_URL}allure/
                """
                
                // Slack通知
                slackSend(
                    channel: env.SLACK_CHANNEL,
                    color: 'warning',
                    message: message
                )
            }
        }
    }
}
