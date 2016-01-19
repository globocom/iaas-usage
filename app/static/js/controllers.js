function RegionCtrl(regionService, $rootScope){
    regionCtrl = this
    regionCtrl.regionList = regionService.listRegions()
    regionCtrl.currentRegion = regionService.getCurrentRegion()

    regionCtrl.listRegions = function(){
        return regionCtrl.regionList
    }

    regionCtrl.changeRegion = function(region){
        if(region.key != regionService.getCurrentRegion().key){
            regionService.changeCurrentRegion(region)
            $rootScope.$broadcast('regionChanged')
        }
    }

    regionCtrl.getCurrentRegion = function(){
        return regionService.getCurrentRegion()
    }
}

function UserCtrl($scope, $http, $window, $state, apiService) {
    userCtrl = this;
    userCtrl.user = null;

    userCtrl.loadUser = function() {
        console.log('Loading user')

        $http({
            method: 'GET',
            url: apiService.builAPIUrl('/current_user/')
        }).then(function successCallback(response){
            userCtrl.user = response.data[0]
            $scope.$broadcast('userLoaded', userCtrl.user);
        });
    }

    $scope.$on('regionChanged', function(){
        $state.go('index.main');
        userCtrl.loadUser()
    })
};

function InstanceCtrl($scope, $http, $stateParams, apiService){
    instanceCtrl = this
    instanceCtrl.title = 'Instances';
    instanceCtrl.projectName = '';
    instanceCtrl.vmCount = []
    instanceCtrl.instances = []

    instanceCtrl.getVmCount = function() {
        console.log('Loading vm count')
        instanceCtrl.projectName = $stateParams.projectName
        $http({
            method: 'GET',
            url: apiService.builAPIUrl('/vm_count/', {project_id: $stateParams.projectId})
        }).then(function successCallback(response){
            instanceCtrl.vmCount = response.data;
        });
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')
        $http({
            method: 'GET',
            url: apiService.builAPIUrl('/virtual_machine/', {project_id: $stateParams.projectId})
        }).then(function successCallback(response){
            instanceCtrl.instances = response.data.virtual_machines;
        });
    }
}

function ProjectCtrl($scope, $http, apiService){
    projectCtrl = this
    projectCtrl.title = 'Instances by project';
    projectCtrl.projects

    projectCtrl.listProjects = function(event, user) {
        user = user || userCtrl.user
        if(angular.isUndefined(this.projects) && user != null){
            console.log('Loading projects')
            $http({
                method: 'GET',
                url: apiService.builAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id})
            }).then(function successCallback(response){
                projectCtrl.projects = response.data;
            });
        }
    }

    $scope.$on('userLoaded', projectCtrl.listProjects)
}

angular
    .module('iaasusage')
    .controller('RegionCtrl', RegionCtrl)
    .controller('UserCtrl', UserCtrl)
    .controller('ProjectCtrl', ProjectCtrl)
    .controller('InstanceCtrl', InstanceCtrl);