/**
 * Jenkins配置脚本
 * 用于自动配置Jenkins实例以支持自动化测试框架
 */

import jenkins.model.*
import hudson.model.*
import hudson.plugins.git.*
import org.jenkinsci.plugins.workflow.job.*
import org.jenkinsci.plugins.workflow.cps.*
import hudson.triggers.*
import hudson.util.*

// 获取Jenkins实例
def jenkins = Jenkins.getInstance()

// 配置全局工具
configureGlobalTools()

// 创建测试任务
createTestJobs()

// 配置系统设置
configureSystemSettings()

// 安装推荐插件
installRecommendedPlugins()

println "✅ Jenkins配置完成！"

/**
 * 配置全局工具
 */
def configureGlobalTools() {
    println "🔧 配置全局工具..."
    
    // 配置Python
    def pythonInstallations = jenkins.getDescriptor("hudson.plugins.python.PythonInstallation")
    if (pythonInstallations) {
        def pythonInstalls = [
            new hudson.plugins.python.PythonInstallation("Python-3.10", "/usr/bin/python3.10", []),
            new hudson.plugins.python.PythonInstallation("Python-3.11", "/usr/bin/python3.11", [])
        ]
        pythonInstallations.setInstallations(pythonInstalls as hudson.plugins.python.PythonInstallation[])
        pythonInstallations.save()
    }
    
    // 配置Allure
    def allureInstallations = jenkins.getDescriptor("ru.yandex.qatools.allure.jenkins.tools.AllureCommandlineInstallation")
    if (allureInstallations) {
        def allureInstalls = [
            new ru.yandex.qatools.allure.jenkins.tools.AllureCommandlineInstallation(
                "Allure-2.24.0", 
                "/usr/local/bin/allure", 
                []
            )
        ]
        allureInstallations.setInstallations(allureInstalls as ru.yandex.qatools.allure.jenkins.tools.AllureCommandlineInstallation[])
        allureInstallations.save()
    }
    
    println "✅ 全局工具配置完成"
}

/**
 * 创建测试任务
 */
def createTestJobs() {
    println "📋 创建测试任务..."
    
    // 主测试Pipeline任务
    createMainTestJob()
    
    // 冒烟测试任务
    createSmokeTestJob()
    
    // 回归测试任务
    createRegressionTestJob()
    
    // 性能测试任务
    createPerformanceTestJob()
    
    // 安全测试任务
    createSecurityTestJob()
    
    println "✅ 测试任务创建完成"
}

/**
 * 创建主测试Pipeline任务
 */
def createMainTestJob() {
    def jobName = "Automated-Testing-Framework"
    def job = jenkins.getItem(jobName)
    
    if (job == null) {
        job = jenkins.createProject(WorkflowJob.class, jobName)
        
        // 设置Pipeline脚本
        def pipelineScript = new CpsFlowDefinition("""
pipeline {
    agent any
    
    parameters {
        choice(name: 'TEST_ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: '选择测试环境')
        choice(name: 'TEST_TYPE', choices: ['all', 'smoke', 'api', 'web', 'regression'], description: '选择测试类型')
        choice(name: 'BROWSER', choices: ['chrome', 'firefox', 'edge'], description: '选择浏览器')
        booleanParam(name: 'HEADLESS', defaultValue: true, description: '是否使用无头模式')
        booleanParam(name: 'PARALLEL_EXECUTION', defaultValue: true, description: '是否并行执行测试')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh 'chmod +x jenkins/jenkins-setup.sh'
                sh './jenkins/jenkins-setup.sh'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    source jenkins.env
                    source venv/bin/activate
                    python run_comprehensive_tests.py --type \${TEST_TYPE}
                '''
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'Test Reports'
            ])
            
            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'reports/allure-results']]
            ])
            
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }
    }
}
        """, true)
        
        job.setDefinition(pipelineScript)
        
        // 设置触发器
        def triggers = [
            new TimerTrigger("H 2 * * *"), // 每天凌晨2点
            new SCMTrigger("H/5 * * * *")  // 每5分钟检查代码变更
        ]
        job.addTrigger(triggers[0])
        job.addTrigger(triggers[1])
        
        job.save()
        println "✅ 创建主测试任务: ${jobName}"
    }
}

/**
 * 创建冒烟测试任务
 */
def createSmokeTestJob() {
    def jobName = "Smoke-Tests"
    def job = jenkins.getItem(jobName)
    
    if (job == null) {
        job = jenkins.createProject(WorkflowJob.class, jobName)
        
        def pipelineScript = new CpsFlowDefinition("""
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh './jenkins/jenkins-setup.sh'
            }
        }
        
        stage('Smoke Tests') {
            steps {
                sh '''
                    source jenkins.env
                    source venv/bin/activate
                    pytest -m smoke --alluredir=reports/allure-results --html=reports/smoke-report.html -v
                '''
            }
        }
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
        """, true)
        
        job.setDefinition(pipelineScript)
        job.save()
        println "✅ 创建冒烟测试任务: ${jobName}"
    }
}

/**
 * 创建回归测试任务
 */
def createRegressionTestJob() {
    def jobName = "Regression-Tests"
    def job = jenkins.getItem(jobName)
    
    if (job == null) {
        job = jenkins.createProject(WorkflowJob.class, jobName)
        
        def pipelineScript = new CpsFlowDefinition("""
pipeline {
    agent any
    
    triggers {
        cron('H 0 * * 0') // 每周日午夜
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh './jenkins/jenkins-setup.sh'
            }
        }
        
        stage('Regression Tests') {
            steps {
                sh '''
                    source jenkins.env
                    source venv/bin/activate
                    pytest -m regression --alluredir=reports/allure-results --html=reports/regression-report.html -v
                '''
            }
        }
    }
}
        """, true)
        
        job.setDefinition(pipelineScript)
        job.save()
        println "✅ 创建回归测试任务: ${jobName}"
    }
}

/**
 * 创建性能测试任务
 */
def createPerformanceTestJob() {
    def jobName = "Performance-Tests"
    def job = jenkins.getItem(jobName)
    
    if (job == null) {
        job = jenkins.createProject(WorkflowJob.class, jobName)
        
        def pipelineScript = new CpsFlowDefinition("""
pipeline {
    agent any
    
    parameters {
        choice(name: 'LOAD_LEVEL', choices: ['light', 'medium', 'heavy'], description: '负载级别')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh './jenkins/jenkins-setup.sh'
            }
        }
        
        stage('Performance Tests') {
            steps {
                sh '''
                    source jenkins.env
                    source venv/bin/activate
                    pytest -m performance --alluredir=reports/allure-results --html=reports/performance-report.html -v
                '''
            }
        }
    }
}
        """, true)
        
        job.setDefinition(pipelineScript)
        job.save()
        println "✅ 创建性能测试任务: ${jobName}"
    }
}

/**
 * 创建安全测试任务
 */
def createSecurityTestJob() {
    def jobName = "Security-Tests"
    def job = jenkins.getItem(jobName)
    
    if (job == null) {
        job = jenkins.createProject(WorkflowJob.class, jobName)
        
        def pipelineScript = new CpsFlowDefinition("""
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh './jenkins/jenkins-setup.sh'
            }
        }
        
        stage('Security Tests') {
            steps {
                sh '''
                    source jenkins.env
                    source venv/bin/activate
                    pytest -m security --alluredir=reports/allure-results --html=reports/security-report.html -v
                '''
            }
        }
    }
}
        """, true)
        
        job.setDefinition(pipelineScript)
        job.save()
        println "✅ 创建安全测试任务: ${jobName}"
    }
}

/**
 * 配置系统设置
 */
def configureSystemSettings() {
    println "⚙️ 配置系统设置..."
    
    // 设置构建保留策略
    def globalBuildDiscarder = new hudson.tasks.LogRotator(30, 100, 7, 20)
    jenkins.setBuildsDiscardPolicy(globalBuildDiscarder)
    
    // 配置邮件通知
    def mailDesc = jenkins.getDescriptor("hudson.tasks.Mailer")
    if (mailDesc) {
        mailDesc.setSmtpHost("smtp.company.com")
        mailDesc.setSmtpPort("587")
        mailDesc.setUseSsl(true)
        mailDesc.setCharset("UTF-8")
        mailDesc.save()
    }
    
    // 配置Slack通知
    def slackDesc = jenkins.getDescriptor("jenkins.plugins.slack.SlackNotifier")
    if (slackDesc) {
        slackDesc.setTeamDomain("your-team")
        slackDesc.setToken("your-slack-token")
        slackDesc.setRoom("#testing")
        slackDesc.save()
    }
    
    jenkins.save()
    println "✅ 系统设置配置完成"
}

/**
 * 安装推荐插件
 */
def installRecommendedPlugins() {
    println "🔌 检查推荐插件..."
    
    def pluginManager = jenkins.getPluginManager()
    def updateCenter = jenkins.getUpdateCenter()
    
    def recommendedPlugins = [
        "workflow-aggregator",      // Pipeline
        "git",                      // Git
        "allure-jenkins-plugin",    // Allure
        "html-publisher",           // HTML Publisher
        "junit",                    // JUnit
        "build-timeout",            // Build Timeout
        "timestamper",              // Timestamper
        "ws-cleanup",               // Workspace Cleanup
        "slack",                    // Slack Notification
        "email-ext",                // Extended Email
        "build-name-setter",        // Build Name Setter
        "parameterized-trigger",    // Parameterized Trigger
        "conditional-buildstep",    // Conditional BuildStep
        "matrix-project",           // Matrix Project
        "python"                    // Python Plugin
    ]
    
    def pluginsToInstall = []
    
    recommendedPlugins.each { pluginName ->
        if (!pluginManager.getPlugin(pluginName)) {
            pluginsToInstall.add(pluginName)
        }
    }
    
    if (pluginsToInstall.size() > 0) {
        println "📦 需要安装的插件: ${pluginsToInstall.join(', ')}"
        println "⚠️ 请手动安装这些插件或使用Jenkins CLI"
    } else {
        println "✅ 所有推荐插件已安装"
    }
}
