pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: '/job_starter/']]]], userRemoteConfigs: [[credentialsId: '6e9fd84c-485a-433e-840b-bf7d449117b3', url: 'git@gitlab.com:radar_bpc/infra/ansible-ps.git']]])
            }
        }
        
        stage('Execute file_watcher.py') {
            steps {
                sh '''
                    echo $BUILD_NUMBER is starting.
                    cd ${WORKSPACE}/job_starter
                    ps -eaf | grep -v grep | grep '/usr/bin/python file_watcher.py' || /usr/bin/python file_watcher.py $BUILD_NUMBER
                '''

            }
        }
    }
}
