pipeline {
    agent any
    environment {
        PYTHON_CMD = 'python3.11'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://kdt-gitlab.elice.io/qa_track/class_03/qa3_final_project/team_02/ioi-lxp.git',
                    credentialsId: 'LXP_GitLab_Repo_Key', 
                    branch: 'develop'
            }
        }
        
        stage('Test') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'LXP_TOKENS', usernameVariable: 'TOKENS_USR', passwordVariable: 'TOKENS_PSW'),
                    usernamePassword(credentialsId: 'LXP_MY_INFO', usernameVariable: 'MY_INFO_USR', passwordVariable: 'MY_INFO_PSW'),
                    usernamePassword(credentialsId: 'LXP_OTHER_INFO', usernameVariable: 'OTHER_INFO_USR', passwordVariable: 'OTHER_INFO_PSW')
                ]) {
                    sh ''' 
                    # 환경변수 이름 맞춰서 재매핑
                    export ELICE_VALID_TOKEN=$TOKENS_USR
                    export ELICE_INVALID_TOKEN=$TOKENS_PSW
        
                    export USER_ID=$MY_INFO_USR
                    export STUDENT_ID=$MY_INFO_PSW
        
                    export INVALID_USER_ID=$OTHER_INFO_USR
                    export OTHER_STUEDNT_ID=$OTHER_INFO_PSW
                    
                    # 1. 가상환경 생성
                    $PYTHON_CMD -m venv venv
                    
                    # 2. 가상환경 활성화 및 의존성 설치
                    . venv/bin/activate
                    pip install --upgrade pip
                    
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    
                    # 3. pytest 실행
                    pytest --junitxml=results.xml || true
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                junit 'results.xml'
            }
        }
    }
}