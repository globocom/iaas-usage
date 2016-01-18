var UserCtrl = function($scope, $http, $stateParams, $state, $q) {
    userCtrl = this;
    
    userCtrl.loadUser = function() {
        console.log('Loading user')
        $http.get('/api/v1/lab/current_user/')
        .success(function(response){
            $scope.user = response[0]
            $scope.$broadcast('userLoaded', $scope.user);
        })
    }
};

function InstanceCtrl($scope, $http, $stateParams, $state){
    var instanceCtrl = this
    this.title = 'Instances';

    instanceCtrl.project = {name: $stateParams.projectName, id: $stateParams.projectId}

    instanceCtrl.listProjects = function(event, user) {
        console.log('Loading projects')
        $http.get('/api/v1/lab/project/?account_name='+ user.account_name +'&domain_id=' + user.domain_id)
        .success(function(response) {
            $scope.projects = response;
        });
    }

    instanceCtrl.getVmCount = function() {
        console.log('Loading vm count')
        $http.get('/api/v1/lab/vm_count/?project_id=' + $stateParams.projectId)
        .success(function(response){
            $scope.vmCount = response;
        })
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')
        $http.get('/api/v1/lab/virtual_machine/?project_id=' + $stateParams.projectId)
        .success(function(response){
            $scope.instances = response.virtual_machines;
        })
    }

    $scope.$on('userLoaded', this.listProjects)
}

angular
    .module('iaasusage')
    .controller('UserCtrl', UserCtrl)
    .controller('InstanceCtrl', InstanceCtrl)