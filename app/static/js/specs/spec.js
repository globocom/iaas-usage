describe('Testing Region controller', function() {

    var rootScope, ctrl;
    var regionServiceMock;
    var region1 = {key: 'r1', value: 'region1'}
    var region2 = {key: 'r2', value: 'region2'}

    var regions = [region1, region2]

    beforeEach(function (done){
        module('iaasusage');
        regionServiceMock = jasmine.createSpyObj('regionService', ['listRegions', 'getCurrentRegion', 'changeCurrentRegion']);

        inject(function($rootScope, $controller) {
            $scope = $rootScope.$new();
            rootScope = $rootScope
            spyOn(rootScope, '$broadcast').and.callThrough();

            regionServiceMock.listRegions.and.returnValue(regions);
            regionServiceMock.getCurrentRegion.and.returnValue(region1);

            ctrl = $controller('RegionCtrl', {
                $scope: $scope,
                $rootScope: $rootScope,
                regionService: regionServiceMock
            });
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should have list of regions and current region populated on controller scope', function() {
        expect(ctrl.regionList).toEqual(regions)
        expect(ctrl.currentRegion).toEqual(region1)
    });

    it('should return the list of regions', function() {
        expect(ctrl.listRegions()).toEqual(regions)
    });

    it('should return the current region', function() {
        expect(ctrl.getCurrentRegion()).toEqual(region1)
    });

    it('should change the current region', function() {
        ctrl.changeRegion(region2)
        expect(regionServiceMock.getCurrentRegion).toHaveBeenCalled();
        expect(regionServiceMock.changeCurrentRegion).toHaveBeenCalled();
        expect(rootScope.$broadcast).toHaveBeenCalledWith('regionChanged');
    });

    it('should change selector when toggleSelector is called', function() {
        expect(ctrl.selectorClass).toBeUndefined()
        ctrl.toggleSelector()
        expect(ctrl.selectorClass).toEqual('sidebar-open')
        ctrl.toggleSelector()
        expect(ctrl.selectorClass).toBeUndefined()
    });

    it('should call toggleSelector when event "regionChanged" is triggered', function() {
        rootScope.$broadcast('regionChanged')
        expect(ctrl.selectorClass).toEqual('sidebar-open')
    });
});

describe('Testing User controller', function() {

    var rootScope, $scope, ctrl, httpBackend, state;
    var apiService;
    var user = {"id": "1", "username": "user"}

    beforeEach(function (done){
        module('iaasusage');

        apiServiceMock = jasmine.createSpyObj('apiService', ['builAPIUrl']);

        inject(function($rootScope, $controller, $http, $state, $httpBackend) {
            $scope = $rootScope.$new();
            httpBackend = $httpBackend
            state = $state
            spyOn($scope, '$broadcast').and.callThrough();
            spyOn($state, 'go').and.callFake(function() { });

            apiServiceMock.builAPIUrl.and.returnValue('/current_user/');

            $httpBackend.when('GET', '/current_user/').respond([user]);

            ctrl = $controller('UserCtrl', {
                $scope: $scope,
                $http: $http,
                $state: $state,
                apiService: apiServiceMock
            });
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should load current logged user from server', function() {
        ctrl.loadUser()
        httpBackend.expectGET('/current_user/');
        httpBackend.flush();
        expect(ctrl.user).toEqual(user)
        expect($scope.$broadcast).toHaveBeenCalledWith('userLoaded', user);
    });

    it('should trigger event when regionChanged event is received', function() {
        $scope.$broadcast('regionChanged')
        expect(state.go).toHaveBeenCalledWith('index.main');
    });
});

describe('Testing Project controller', function() {

    var projects = [{"id":1, "name": "name","vm_count":1, "account": "account"}]
    var user = {"username": "user", "account_name": "acc", "domain_id": 1, "is_admin": false}
    var ctrl, httpBackend, $scope

    beforeEach(function (done){
        module('iaasusage');

        apiServiceMock = jasmine.createSpyObj('apiService', ['builAPIUrl']);

        inject(function($rootScope, $controller, $http, $httpBackend) {
            $scope = $rootScope.$new();
            httpBackend = $httpBackend

            apiServiceMock.builAPIUrl.and.returnValue('/project/');

            $httpBackend.when('GET', '/project/').respond(projects);

            ctrl = $controller('ProjectCtrl', {
                $scope: $scope,
                $http: $http,
                apiService: apiServiceMock,
                DTOptionsBuilder: {newOptions: function(){}}
            });
        });

        window.jasmine.DEFAULT_TIMEOUT_INTERVAL = 60000;
        return setTimeout((function() { return done(); }), 500);
    });

    it('should return the list of projects', function() {
        ctrl.listProjects(null, user)
        httpBackend.expectGET('/project/');
        httpBackend.flush();
        expect(ctrl.projects).not.toBeUndefined()
    });
});