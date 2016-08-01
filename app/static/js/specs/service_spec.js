describe('Testing ListFilterService', function() {

    var service;

    beforeEach(function (done){
        module('iaasusage');
        inject(function(listFilterService) {
            service = listFilterService;
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should filter list by key and value', function() {
        var list = [{zone_id: 1}, {zone_id:2}];
        var filters = {};
        var result = service.filter(list, filters, 'zone_id', 2);

        expect(result.length).toEqual(1);
        expect(result[0]).toEqual({zone_id:2});
        expect(filters).toEqual({zone_id: 2});
    });

    it('should remove filter', function() {
        var list = [{zone_id: 1}, {zone_id:2}];
        var filters = {};
        service.filter(list, filters, 'zone_id', 2);
        var result = service.filter(list, filters, 'zone_id', 2);

        expect(result.length).toEqual(2);
        expect(filters).toEqual({});
    });
});

describe('Testing TagService', function() {

    var service;

    beforeEach(function (done){
        module('iaasusage');
        inject(function(tagService) {
            service = tagService;
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should build tag parameters', function() {
        var tags = service.buildTagParams([{key: 'tagA', value: 1}, {key: 'tagB', value: 2}])
        expect(tags).toEqual({'tags[0].key': 'tagA', 'tags[0].value': 1, 'tags[1].key': 'tagB', 'tags[1].value': 2})
    });
});

describe('Testing RegionService', function() {

    var service;

    beforeEach(function (done){
        module('iaasusage');
        inject(function(regionService, $rootScope) {
            $rootScope.regions = [{key: 'cme', value: 'RJCME'}, {key: 'cta', value: 'RJCTA'}]
            service = regionService;
            $scope = $rootScope.$new();
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should return the default region', function() {
        var region = service.getCurrentRegion()
        expect(region).toEqual({key: 'cme', value: 'RJCME'})
    });

    it('should list all regions', function() {
        var regions = service.listRegions()
        expect(regions.length).toEqual(2)
    });
});

describe('Testing ApiService', function() {

    var service;

    beforeEach(function (done){
        module('iaasusage', function($provide){
            regionServiceMock = jasmine.createSpyObj('regionService', ['getCurrentRegion']);
            regionServiceMock.getCurrentRegion.and.returnValue({key: 'r1', value: 'region1'});
            $provide.value("regionService", regionServiceMock);
        });

        inject(function(apiService) {
            service = apiService;
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should return the service url for a given region', function() {
        var uri = service.buildAPIUrl('/storage/')
        expect(uri).toEqual('/api/v1/r1/storage/')
    });

    it('should return the sevice url with query string', function() {
        var uri = service.buildAPIUrl('/storage/', {param1: 'a', param2: 'b'})
        expect(uri).toEqual('/api/v1/r1/storage/?param1=a&param2=b')
    });
});