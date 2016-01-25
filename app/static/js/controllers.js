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
            regionCtrl.toggleSelector()
        }
    }

    regionCtrl.toggleSelector = function(){
        if(angular.isUndefined(regionCtrl.selectorClass)){
            regionCtrl.selectorClass = 'sidebar-open'
        }else{
            regionCtrl.selectorClass = undefined
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

function InstanceCtrl($scope, $http, $stateParams, $filter, apiService, DTOptionsBuilder){
    instanceCtrl = this
    instanceCtrl.title = 'Instances';
    instanceCtrl.projectName = '';
    instanceCtrl.vmCount = []
    instanceCtrl.instances = []
    instanceCtrl.instanceView = []
    instanceCtrl.filters = {}
    instanceCtrl.tags = []

    $scope.dtOptions = DTOptionsBuilder.newOptions()
    .withDOM('<"html5buttons"B>lTfgitp')
    .withButtons([{extend: 'copy'}, {extend: 'csv'}]);

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
            url: apiService.builAPIUrl('/virtual_machine/', params)
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
            instanceCtrl.instanceView = $filter('filter')(instanceCtrl.instances, instanceCtrl.filters)
        }else{
            delete instanceCtrl.filters[field]
            var filter = {}
            filter[field] = value
            $.extend(instanceCtrl.filters, filter)
            instanceCtrl.instanceView = $filter('filter')(instanceCtrl.instances, instanceCtrl.filters)
        }
    }

    instanceCtrl.clearFilters = function(){
        instanceCtrl.filters = {}
        instanceCtrl.instances
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

    instanceCtrl.removeTag = function(key, value){
        for(var i = 0 ; i < instanceCtrl.tags.length ; i++){
            console.log(instanceCtrl.tags[i].key == key)
            console.log(instanceCtrl.tags[i].value == value)
            if(instanceCtrl.tags[i].key == key && instanceCtrl.tags[0].value == value){
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
                url: apiService.builAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id, is_admin: user.is_admin})
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