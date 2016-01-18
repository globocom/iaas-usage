/**
 * INSPINIA - Responsive Admin Theme
 *
 * Inspinia theme use AngularUI Router to manage routing and views
 * Each view are defined as state.
 * Initial there are written state for all view in theme.
 *
 */
function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider) {
    $urlRouterProvider.otherwise('/index/main');

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });
    var staticPrefix = 'static/'
    var viewPrefix = staticPrefix + 'views/';

    $stateProvider
        .state('index', {
            abstract: true,
            url: '/index',
            templateUrl: viewPrefix + 'common/content.html'
        })
        .state('index.main', {
            url: '/main',
            templateUrl: viewPrefix + 'main.html',
        })
        .state('index.instances', {
            abstract: true,
            url: '/instances',
            templateUrl: viewPrefix + 'instances/index.html'
        })
        .state('index.instances.vm_count', {
            url: '/:projectName/:projectId',
            templateUrl: viewPrefix + 'instances/vm_count.html'
        })
        .state('index.projects', {
            abstract: true,
            url: '/projects',
            templateUrl: viewPrefix + 'projects/index.html'
        })
        .state('index.projects.list',{
            url: '',
            templateUrl: viewPrefix + 'projects/list.html',
        })
}
angular
    .module('iaasusage')
    .config(config)
    .run(function($rootScope, $state) {
        $rootScope.$state = $state;
    });
