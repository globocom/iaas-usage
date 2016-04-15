function RegionService($rootScope, $stateParams, $filter, $stateParams, $state) {
    var regions =  [
        {key: 'ebt', value: 'RJEBT'},
        {key: 'cta', value: 'RJCTA'},
        {key: 'cme', value: 'RJCME'},
    ]

    return {
        listRegions: function() {
            return regions
        },
        getCurrentRegion: function(){
            if($stateParams.region){
                $rootScope.region = $filter('filter')(regions, {key: $stateParams.region})[0]
            }
            if(!$rootScope.region){
                $rootScope.region = regions[0]
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
            fullUri = '/api/v1/'+ regionService.getCurrentRegion().key + uri + query
            return fullUri
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

angular
    .module('iaasusage')
    .service('regionService', RegionService)
    .service('tagService', TagService)
    .service('listFilterService', ListFilterService)
    .service('userService', UserService)
    .service('resourceLimitService', ResourceLimitService)
    .service('apiService', ApiService);