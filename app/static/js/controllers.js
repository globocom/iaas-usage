var UserCtrl = function($scope, $http, $stateParams, $state, $q) {
    userCtrl = this;
    userCtrl.user = null;

    userCtrl.loadUser = function() {
        console.log('Loading user')
        $http.get('/api/v1/lab/current_user/')
        .success(function(response){
            userCtrl.user = response[0]
            $scope.$broadcast('userLoaded', $scope.user);
        })
    }
};

function InstanceCtrl($scope, $http, $stateParams, $state){
    instanceCtrl = this
    this.title = 'Instances';
    instanceCtrl.projectName = '';
    instanceCtrl.vmCount = []
    instanceCtrl.instances = []

    instanceCtrl.getVmCount = function() {
        instanceCtrl.projectName = $stateParams.projectName
        console.log('Loading vm count')
        $http.get('/api/v1/lab/vm_count/?project_id=' + $stateParams.projectId)
        .success(function(response){
            instanceCtrl.vmCount = response;
        })
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')
        $http.get('/api/v1/lab/virtual_machine/?project_id=' + $stateParams.projectId)
        .success(function(response){
            instanceCtrl.instances = response.virtual_machines;
        })
    }

    $scope.$on('userLoaded', this.listProjects)
}

function ProjectCtrl($scope, $http, $stateParams){
    projectCtrl = this
    projectCtrl.title = 'Instances by project';
    projectCtrl.projects

    projectCtrl.listProjects = function(event, user) {
        user = user || userCtrl.user
        if(angular.isUndefined(this.projects) && user != null){
            console.log('Loading projects')
            $http.get('/api/v1/lab/project/?account_name='+ user.account_name +'&domain_id=' + user.domain_id)
            .success(function(response) {
                projectCtrl.projects = response;
            });
        }
    }

    $scope.$on('userLoaded', this.listProjects)
}

angular
    .module('iaasusage')
    .controller('UserCtrl', UserCtrl)
    .controller('ProjectCtrl', ProjectCtrl)
    .controller('InstanceCtrl', InstanceCtrl)