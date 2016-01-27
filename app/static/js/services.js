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
        buildAPIUrl: function(uri, params) {
            query = params ? '?' + $.param(params) : '';
            fullUri = '/api/v1/'+ regionService.getCurrentRegion().key + uri + query
            return fullUri
        }
    };
}

angular
    .module('iaasusage')
    .service('regionService', RegionService)
    .service('apiService', ApiService);