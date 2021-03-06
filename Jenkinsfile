#!/usr/bin/env groovy

app_linux_libs = "_deps/dgl*.whl"
// Currently Windows is not working with Cython yet
app_win64_libs = "_deps\\dgl*.whl"

app = "myapp"

def init_git() {
  sh "rm -rf *"
  checkout scm
  sh "git submodule update --recursive --init"
}

def init_git_win64() {
  checkout scm
  bat "git submodule update --recursive --init"
}

// pack libraries for later use
def pack_dgl(name, libs) {
  echo "Packing ${libs} into ${name}"
  stash includes: libs, name: name
}

// unpack libraries saved before
def unpack_dgl(name, libs) {
  unstash name
  echo "Unpacked ${libs} from ${name}"
}

def build_linux(dev) {
  init_git()
  sh "bash tests/scripts/build.sh ${dev}"
  pack_dgl("app-${dev}-linux", app_linux_libs)
}

def build_win64(dev) {
  /* Assuming that Windows slaves are already configured with MSBuild VS2017,
   * CMake and Python/pip/setuptools etc. */
  init_git_win64()
  bat "CALL tests\\scripts\\build.bat"
  pack_dgl("app-${dev}-win64", app_win64_libs)
}

def unit_test_linux(backend, dev) {
  init_git()
  unpack_dgl("app-${dev}-linux", app_linux_libs)
  timeout(time: 10, unit: 'MINUTES') {
    sh "bash tests/scripts/task_unit_test.sh ${backend} ${dev}"
  }
}

def unit_test_win64(backend, dev) {
  init_git_win64()
  unpack_dgl("app-${dev}-win64", app_win64_libs)
  timeout(time: 2, unit: 'MINUTES') {
    bat "CALL tests\\scripts\\task_unit_test.bat ${backend}"
  }
}

def example_test_linux(backend, dev) {
  init_git()
  unpack_dgl("app-${dev}-linux", app_linux_libs)
  timeout(time: 20, unit: 'MINUTES') {
    sh "bash tests/scripts/task_example_test.sh ${dev}"
  }
}

def example_test_win64(backend, dev) {
  init_git_win64()
  unpack_dgl("app-${dev}-win64", app_win64_libs)
  timeout(time: 20, unit: 'MINUTES') {
    bat "CALL tests\\scripts\\task_example_test.bat ${dev}"
  }
}

//def tutorial_test_linux(backend) {
//  init_git()
//  unpack_dgl("app-cpu-linux", app_linux_libs)
//  timeout(time: 20, unit: 'MINUTES') {
//    sh "bash tests/scripts/task_${backend}_tutorial_test.sh"
//  }
//}

pipeline {
  agent any
  stages {
    stage("Lint Check") {
      agent { 
        docker {
          label "linux-cpu-node"
          image "dgllib/dgl-ci-lint" 
        }
      }
      steps {
        init_git()
        sh "bash tests/scripts/task_lint.sh"
      }
      post {
        always {
          cleanWs disableDeferredWipeout: true, deleteDirs: true
        }
      }
    }
    stage("Build") {
      parallel {
        stage("CPU Build") {
          agent { 
            docker {
              label "linux-cpu-node"
              image "dgllib/${app}-ci-cpu:02192020" 
            }
          }
          steps {
            build_linux("cpu")
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        stage("GPU Build") {
          agent {
            docker {
              label "linux-cpu-node"
              image "dgllib/${app}-ci-gpu:02192020"
              //args "-u root"
            }
          }
          steps {
            build_linux("gpu")
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        //stage("CPU Build (Win64)") {
        //  // Windows build machines are manually added to Jenkins master with
        //  // "windows" label as permanent agents.
        //  agent { label "windows" }
        //  steps {
        //    build_win64("cpu")
        //  }
        //  post {
        //    always {
        //      cleanWs disableDeferredWipeout: true, deleteDirs: true
        //    }
        //  }
        //}
        // Currently we don't have Windows GPU build machines
      }
    }
    stage("Test") {
      parallel {
        stage("Tensorflow CPU") {
          agent { 
            docker {
              label "linux-cpu-node"
              image "dgllib/${app}-ci-cpu:02192020" 
            }
          }
          stages {
            stage("Unit test") {
              steps {
                unit_test_linux("tensorflow", "cpu")
              }
            }
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        stage("Tensorflow GPU") {
          agent { 
            docker { 
              label "linux-gpu-node"
              image "dgllib/${app}-ci-gpu:02192020" 
              args "--runtime nvidia"
            }
          }
          stages {
            stage("Unit test") {
              steps {
                sh "nvidia-smi"
                unit_test_linux("tensorflow", "gpu")
              }
            }
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        stage("Torch CPU") {
          agent { 
            docker {
              label "linux-cpu-node"
              image "dgllib/${app}-ci-cpu:02192020" 
            }
          }
          stages {
            stage("Unit test") {
              steps {
                unit_test_linux("pytorch", "cpu")
              }
            }
            stage("Example test") {
              steps {
                example_test_linux("pytorch", "cpu")
              }
            }
            //stage("Tutorial test") {
            //  steps {
            //    tutorial_test_linux("pytorch")
            //  }
            //}
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        //stage("Torch CPU (Win64)") {
        //  agent { label "windows" }
        //  stages {
        //    stage("Unit test") {
        //      steps {
        //        unit_test_win64("pytorch", "cpu")
        //      }
        //    }
        //    stage("Example test") {
        //      steps {
        //        example_test_win64("pytorch", "cpu")
        //      }
        //    }
        //  }
        //  post {
        //    always {
        //      cleanWs disableDeferredWipeout: true, deleteDirs: true
        //    }
        //  }
        //}
        stage("Torch GPU") {
          agent {
            docker {
              label "linux-gpu-node"
              image "dgllib/${app}-ci-gpu:02192020"
              args "--runtime nvidia"
            }
          }
          stages {
            stage("Unit test") {
              steps {
                sh "nvidia-smi"
                unit_test_linux("pytorch", "gpu")
              }
            }
            stage("Example test") {
              steps {
                example_test_linux("pytorch", "gpu")
              }
            }
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        stage("MXNet CPU") {
          agent { 
            docker {
              label "linux-cpu-node"
              image "dgllib/${app}-ci-cpu:02192020" 
            }
          }
          stages {
            stage("Unit test") {
              steps {
                unit_test_linux("mxnet", "cpu")
              }
            }
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
        stage("MXNet GPU") {
          agent {
            docker {
              label "linux-gpu-node" 
              image "dgllib/${app}-ci-gpu:02192020"
              args "--runtime nvidia"
            }
          }
          stages {
            stage("Unit test") {
              steps {
                sh "nvidia-smi"
                unit_test_linux("mxnet", "gpu")
              }
            }
          }
          post {
            always {
              cleanWs disableDeferredWipeout: true, deleteDirs: true
            }
          }
        }
      }
    }
  }
  post {
    always {
      node('windows') {
        bat "rmvirtualenv ${BUILD_TAG}"
      }
    }
  }
}
