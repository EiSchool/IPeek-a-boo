// The same pipeline for Jenkins, kept for comparison with GitHub Actions
// (.github/workflows/ci.yml is the one the team uses). Needs a Jenkins agent
// with Python 3.10+ and a GitHub webhook pointing at Jenkins.

pipeline {
    agent any
    triggers { githubPush() }
    options { timeout(time: 10, unit: 'MINUTES') }

    stages {
        stage('Install') {
            steps {
                sh 'python3 -m venv .ci-venv'
                sh '.ci-venv/bin/pip install -r requirements-dev.txt'
            }
        }
        stage('Lint') {
            steps { sh '.ci-venv/bin/python -m flake8 . --exclude .ci-venv,.venv,exports' }
        }
        stage('Test') {
            steps {
                sh '.ci-venv/bin/python -m coverage run -m unittest -v'
                sh '.ci-venv/bin/python -m coverage report'
            }
        }
    }
    post {
        always { sh '.ci-venv/bin/python -m coverage html || true' }
        success { echo 'All checks passed - safe to merge.' }
        failure { echo 'Pipeline failed - do not merge.' }
    }
}
