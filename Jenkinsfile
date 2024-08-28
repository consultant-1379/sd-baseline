pipeline {
    agent {
        node {
            label 'sa_slave'
        }
    }

    parameters {
        string(name: 'CHART_NAME', defaultValue: '')
        string(name: 'CHART_VERSION', defaultValue: '')
        string(name: 'CHART_REPO', defaultValue: '')
        string(name: 'KUBERNETES_CONFIG_FILE_NAME', defaultValue: 'kube.config.rontgen020')
    }

    environment {
        GIT_CMD = "docker run --rm -v ${env.WORKSPACE}:/git alpine/git"
        HELM_CMD = "docker run --rm -v ${env.WORKSPACE}/.kube/config:/root/.kube/config -v ${env.WORKSPACE}/helm-home:/root/.helm -v ${env.WORKSPACE}:${env.WORKSPACE} linkyard/docker-helm:2.8.2"
        BASELINE_CHART_REPO_URL = "https://arm.epk.ericsson.se/artifactory/proj-orchestration-sd-helm/"
    }
 
    stages {
        stage('Clean') {
            steps {
                //sh '${HELM_CMD} del --purge sd-assurance'
                sh '${GIT_CMD} clean -xdff'
            }
        }

        stage('Inject Kubernetes Configuration File') {
            steps {
                configFileProvider([configFile(fileId: "${env.KUBERNETES_CONFIG_FILE_NAME}", targetLocation: "${env.WORKSPACE}/.kube/")]) {
              }
           }
       }

        stage('Prepare Helm') {
            steps {
                sh 'mkdir helm-home'
                sh '${HELM_CMD} init --client-only'
                sh '${HELM_CMD} repo add baseline-repo $BASELINE_CHART_REPO_URL'
                sh '${HELM_CMD} repo update'
            }
        }

        stage('Initial Install Last Good Version of Baseline Chart') {
            steps {
                sh '${HELM_CMD} list -a'    
            	sh '${HELM_CMD} search baseline-repo'
                sh '${HELM_CMD} upgrade --install --debug --wait --timeout 1200 staging baseline-repo/sd --namespace staging --set eric-data-message-bus-kf.external_access.extHostName="rontgen020.rnd.gic.ericsson.se" --set ingress.hostname="staging.rontgen020.rnd.gic.ericsson.se" --set api-gateway.cluster.realm="http://staging.rontgen020.rnd.gic.ericsson.se" --set api-gateway.forgerock.uri="http://ieatdo9034-om-2.athtem.eei.ericsson.se:8080/" --set ocwf-micro.ecmConfig.ecmUrl="ieatdo9034-om-2.athtem.eei.ericsson.se:8080" --set ocwf-micro.ecmConfig.tenantId="ECM" --set ocwf-micro.ecmConfig.authHeader="Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw==" --set eric-data-visualizer-kb.ingress.hosts="{eric-data-visualizer-kb.rontgen020.rnd.gic.ericsson.se}"' 
                //sh '${HELM_CMD} search baseline-repo' 
            }
         }

        stage('Update Chart Requirements File') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "sd-baseline/scripts/update_chart_requirements.py --appChartDir=${env.WORKSPACE}/sd-baseline/charts/sd --chartName=${CHART_NAME} --chartRepo=${CHART_REPO} --chartVersion=${CHART_VERSION}"
            }
        }

        stage('Increment Chart Version Locally') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "sd-baseline/scripts/increment_chart_version.py --appChartDir=${env.WORKSPACE}/sd-baseline/charts/sd"
            } 
        }

        stage('Download Chart Requirements') {
            steps {
                sh "sd-baseline/scripts/download_chart_requirements.py --appChartDir=${env.WORKSPACE}/sd-baseline/charts/sd --helmCommand='${HELM_CMD}'"
            }
        }

        stage('Upgrade to Updated Chart') {
            steps {
                sh "${HELM_CMD} upgrade --wait --timeout 1200 staging ${env.WORKSPACE}/sd-baseline/charts/sd --set eric-data-message-bus-kf.external_access.extHostName='rontgen020.rnd.gic.ericsson.se' --set ingress.hostname='staging.rontgen020.rnd.gic.ericsson.se' --set api-gateway.cluster.realm='http://staging.rontgen020.rnd.gic.ericsson.se' --set api-gateway.forgerock.uri='http://ieatdo9034-om-2.athtem.eei.ericsson.se:8080/' --set ocwf-micro.ecmConfig.ecmUrl='ieatdo9034-om-2.athtem.eei.ericsson.se' --set ocwf-micro.ecmConfig.tenantId='ECM' --set ocwf-micro.ecmConfig.authHeader='Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw==' --set eric-data-visualizer-kb.ingress.hosts='{eric-data-visualizer-kb.rontgen020.rnd.gic.ericsson.se}'"
            }
        }

        stage('Final Integration Tests') {
            steps {
                sh 'echo Tests Go Here'
            }
        }

        stage('Commit Changes in Baseline Repo') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "sd-baseline/scripts/commit_chart_changes.py --appChartDir=${env.WORKSPACE}/sd-baseline/charts/sd"
            }
        }

        stage('Upload Chart to ARM') {
            when {
                expression { params.CHART_NAME != "" }
            }
            steps {
                sh "python sd-baseline/scripts/uploadScript.py -w ${env.WORKSPACE} --repoRoot=${env.WORKSPACE}/sd-baseline/charts --appChartDir=sd  --appHelmRepo=$BASELINE_CHART_REPO_URL --helm='${HELM_CMD}'"
            }
        }
    }
}
