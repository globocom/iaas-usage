function RegionService($rootScope, $stateParams, $filter, $stateParams, $state) {
    return {
        listRegions: function() {
           return $rootScope.regions
        },
        getCurrentRegion: function(){
            if($stateParams.region){
                $rootScope.region = $filter('filter')($rootScope.regions, {key: $stateParams.region})[0]
            }
            if(!$rootScope.region){
                $rootScope.region = $rootScope.regions[0]
            }
           return $rootScope.region
        },
        reloadWithRegion: function(region){
            var stateName = $state.current.name
            if(stateName == 'index.storage' || stateName == 'index.instances' || stateName == 'index.quota'){
                stateName = stateName + '_projects'
            }
            $state.go(stateName, {region: region});
        }
    };
}

function ApiService(regionService) {
    return {
        buildAPIUrl: function(uri, params) {
            query = params ? '?' + $.param(params) : '';
            return '/api/v1/'+ regionService.getCurrentRegion().key + uri + query
        }
    };
}

function TagService() {
    return {
        buildTagParams: function(tags) {
            var params = {}
            if(tags.length > 0){
                for(var i = 0 ; i < tags.length ; i++){
                    params['tags['+ i + '].key'] = tags[i].key
                    params['tags['+ i + '].value'] = tags[i].value
                }
            }
            return params;
        }
    };
}

function ListFilterService($filter){
    return {
        filter: function(list, filters, field, value){
            var filteredList = []
            if(filters[field] == value){
                delete filters[field]
                filteredList = $filter('filter')(list, filters, function(actual, expected){
                    if(actual == null){
                        return false;
                    }
                    return actual.toString().toLowerCase() == expected.toString().toLowerCase();
                });
            }else{
                delete filters[field]
                var filter = {}
                filter[field] = value
                $.extend(filters, filter)
                filteredList = $filter('filter')(list, filters, function(actual, expected){
                    if(actual == null){
                        return false;
                    }
                    return actual.toString().toLowerCase() == expected.toString().toLowerCase();
                })
            }
            return filteredList
        }
    }
}

function UserService($rootScope, $http, apiService, regionService) {
    return{
        getCurrentUser: function(callback){
            $http({
                method: 'GET',
                url: apiService.buildAPIUrl('/current_user/')
            }).then(function successCallback(response){
                $rootScope.currentUser = response.data
                callback(response.data)
            });
        }
    }
}

function ResourceLimitService($http, userService, apiService) {
    return {
        getResourceLimits: function(projectId, callback){
            userService.getCurrentUser(function(user){
                $http({
                    method: 'GET',
                    url: apiService.buildAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id, id: projectId, is_admin: user.is_admin})
                }).then(function successCallback(response){
                    callback(response.data[0])
                });
            })
        }
    }
}

function ServiceOfferingService($rootScope, $http, $filter, apiService){
    return {
        getServiceOffering: function(name, callback){
            if(angular.isUndefined($rootScope.offerings)){
                $http({
                    cache: true,
                    method: 'GET',
                    url: apiService.buildAPIUrl('/service_offering/')
                }).then(function successCallback(response){
                    $rootScope.offerings = response.data
                    callback($filter('filter')($rootScope.offerings, {name: name})[0])
                });
            }else{
                callback($filter('filter')($rootScope.offerings, {name: name})[0])
            }
        }
    }
}

function ServiceOfferingTooltip(serviceOfferingService){
    return {
        restrict: 'E',
        replace: 'false',
        template: "<a data-toggle='offering-tip' data-placement='top' data-original-title='{{title}}'>{{name}}</a>",
        link: function(scope, elem, attrs) {
            serviceOfferingService.getServiceOffering(attrs.name, function(offering){
                scope.name = attrs.name
                if(offering){
                    scope.title = "CPU Cores: " + offering.cpu_number + " <br/> CPU Speed: "+ offering.cpu_speed +" MHz <br/>RAM: "+ offering.memory +" MB"
                    $('[data-toggle="offering-tip"]').tooltip({html: true});
                }
            })
        }
    };
}

angular
    .module('iaasusage')
    .service('regionService', RegionService)
    .service('tagService', TagService)
    .service('listFilterService', ListFilterService)
    .service('userService', UserService)
    .service('resourceLimitService', ResourceLimitService)
    .service('apiService', ApiService)
    .service('serviceOfferingService', ServiceOfferingService)
    .directive('serviceOfferingTooltip', ServiceOfferingTooltip);