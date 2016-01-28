function RegionCtrl(regionService, $rootScope, $scope){

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

    regionCtrl.toggleSelector = function(){
        regionCtrl.selectorClass = angular.isUndefined(regionCtrl.selectorClass) ? 'sidebar-open' : undefined
    }

    regionCtrl.getCurrentRegion = function(){
        return regionService.getCurrentRegion()
    }

    $scope.$on('regionChanged', function(){
        regionCtrl.toggleSelector()
    })
}

function UserCtrl($scope, $http, $state, apiService) {

    userCtrl = this;
    userCtrl.user = null;

    userCtrl.loadUser = function(callback) {
        console.log('Loading user')

        $http({
            method: 'GET',
            url: apiService.buildAPIUrl('/current_user/')
        }).then(function successCallback(response){
            userCtrl.user = response.data[0]
            $scope.$broadcast('userLoaded', userCtrl.user);
            if(angular.isDefined(callback)){
                callback()
            }
        });
    }

    $scope.$on('regionChanged', function(){
        userCtrl.loadUser(function(){
            $state.go('index.projects');
        })
    })
};

function InstanceCtrl($scope, $http, $stateParams, $filter, apiService, DTOptionsBuilder){

    instanceCtrl = this
    instanceCtrl.title = 'Instances';
    instanceCtrl.projectName = '';
    instanceCtrl.vmCount
    instanceCtrl.instances = []
    instanceCtrl.instanceView = []
    instanceCtrl.filters = {}
    instanceCtrl.tags = []

    $scope.dtOptions = DTOptionsBuilder.newOptions()
    .withDOM('<"html5buttons"B>lTfgitp')
    .withButtons([{extend: 'copy'}, {extend: 'csv'}]);

    instanceCtrl.getInstances = function(){
        return instanceCtrl.instanceView
    }

    instanceCtrl.getVmCount = function(){
        return instanceCtrl.vmCount
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')

        instanceCtrl.projectName = $stateParams.projectName
        var params = {project_id: $stateParams.projectId}
        if(instanceCtrl.tags.length > 0){
            for(var i = 0 ; i < instanceCtrl.tags.length ; i++){
                params['tags['+ i + '].key'] = instanceCtrl.tags[i].key
                params['tags['+ i + '].value'] = instanceCtrl.tags[i].value
            }
        }
        $http({
            method: 'GET',
            url: apiService.buildAPIUrl('/virtual_machine/', params)
        }).then(function successCallback(response){
            instanceCtrl.instances = response.data.vms.virtual_machines;
            instanceCtrl.instanceView = instanceCtrl.instances;
            instanceCtrl.vmCount = response.data.summary;
            if(instanceCtrl.instances.length == 0){
                toastr.warning("No virtual machines were found for selected filter.");
            }
        });
    }

    instanceCtrl.filter = function(field, value){
        console.log('Filter virtual machine list. field: ' + field + ' value: ' + value)

        if(instanceCtrl.filters[field] == value){
            delete instanceCtrl.filters[field]
            instanceCtrl.instanceView = $filter('filter')(instanceCtrl.instances, instanceCtrl.filters, function(actual, expected){
                return actual.toLowerCase() == expected.toLowerCase();
            });
        }else{
            delete instanceCtrl.filters[field]
            var filter = {}
            filter[field] = value
            $.extend(instanceCtrl.filters, filter)
            instanceCtrl.instanceView = $filter('filter')(instanceCtrl.instances, instanceCtrl.filters, function(actual, expected){
                return actual.toLowerCase() == expected.toLowerCase();
            })
        }
    }

    instanceCtrl.clearFilters = function(){
        instanceCtrl.filters = {}
    }

    instanceCtrl.isFilteredField = function(field, value){
        return instanceCtrl.filters[field] == value
    }

    instanceCtrl.filterByTag = function(key, value){
        instanceCtrl.tags.push({key: key, value: value})
        instanceCtrl.tagKey = null;
        instanceCtrl.tagValue = null;
        instanceCtrl.clearFilters()
        instanceCtrl.listVirtualMachines()
    }

    instanceCtrl.removeTagFilter = function(key, value){
        for(var i = 0 ; i < instanceCtrl.tags.length ; i++){
            if(instanceCtrl.tags[i].key == key && instanceCtrl.tags[i].value == value){
                instanceCtrl.tags.splice(i, 1);
            }
        }
        instanceCtrl.listVirtualMachines()
    }
}

function ProjectCtrl($scope, $http, apiService, DTOptionsBuilder){

    projectCtrl = this
    projectCtrl.title = 'Instances by project';
    projectCtrl.projects

    $scope.dtOptions = DTOptionsBuilder.newOptions()

    projectCtrl.listProjects = function(event, user) {
        user = user || userCtrl.user
        if(angular.isUndefined(this.projects) && user != null){
            console.log('Loading projects')

            $http({
                method: 'GET',
                url: apiService.buildAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id, is_admin: user.is_admin})
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