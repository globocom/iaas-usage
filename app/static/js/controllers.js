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
        $http.get(apiService.builAPIUrl('/current_user/'))
        .success(function(response){
            userCtrl.user = response[0]
            $scope.$broadcast('userLoaded', $scope.user);
        })
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
        $http.get(apiService.builAPIUrl('/vm_count/', {project_id: $stateParams.projectId}))
        .success(function(response){
            instanceCtrl.vmCount = response;
        })
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')
        $http.get(apiService.builAPIUrl('/virtual_machine/', {project_id: $stateParams.projectId}))
        .success(function(response){
            instanceCtrl.instances = response.virtual_machines;
        })
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
            $http.get(apiService.builAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id}))
            .success(function(response) {
                projectCtrl.projects = response;
            });
        }
    }

    $scope.$on('userLoaded', projectCtrl.listProjects)
}

function RegionService($rootScope) {
    return {
        listRegions: function() {
            return [
                {key: 'ebt', value: 'RJEBT'},
                {key: 'cta', value: 'RJCTA'},
                {key: 'lab', value: 'RJLAB'}
            ]
        },
        getCurrentRegion: function(){
           return ($rootScope.currentRegion || {key: 'ebt', value: 'RJEBT'})
        },
        changeCurrentRegion: function(region){
            $rootScope.currentRegion = region
        }
    };
}

function ApiService(regionService) {
    return {
        builAPIUrl: function(uri, params) {
            query = params ? '?' + $.param(params) : '';
            fullUri = '/api/v1/'+ regionService.getCurrentRegion().key + uri + query
            return fullUri
        }
    };
}

angular
    .module('iaasusage')
    .controller('RegionCtrl', RegionCtrl)
    .controller('UserCtrl', UserCtrl)
    .controller('ProjectCtrl', ProjectCtrl)
    .controller('InstanceCtrl', InstanceCtrl)
    .factory('regionService', RegionService)
    .factory('apiService', ApiService);