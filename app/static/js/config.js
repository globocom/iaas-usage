/**
 * INSPINIA - Responsive Admin Theme
 *
 * Inspinia theme use AngularUI Router to manage routing and views
 * Each view are defined as state.
 * Initial there are written state for all view in theme.
 *
 */

var staticPrefix = 'static/'
var viewPrefix = staticPrefix + 'views/';

function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider) {
    $urlRouterProvider.otherwise('/index/main');

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });

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
            templateUrl: viewPrefix + 'instances/vm_count.html',
            resolve: {
                loadPlugin: loadDataTablePlugin
            }
        })
        .state('index.projects', {
            abstract: true,
            url: '/projects',
            templateUrl: viewPrefix + 'projects/index.html'
        })
        .state('index.projects.list',{
            url: '',
            templateUrl: viewPrefix + 'projects/list.html',
            resolve: {
                loadPlugin: loadDataTablePlugin
            }
        })
}

function loadDataTablePlugin($ocLazyLoad) {
    return $ocLazyLoad.load([
        {
            serie: true,
            files: [staticPrefix + 'js/plugins/dataTables/datatables.min.js',
                    staticPrefix + 'css/plugins/dataTables/datatables.min.css']
        },
        {
            serie: true,
            name: 'datatables',
            files: [staticPrefix + 'js/plugins/dataTables/angular-datatables.min.js']
        },
        {
            serie: true,
            name: 'datatables.buttons',
            files: [staticPrefix + 'js/plugins/dataTables/angular-datatables.buttons.min.js']
        }
    ]);
}

function HttpErrorInterceptor($httpProvider) {
    $httpProvider.interceptors.push(function() {
        return {
            responseError: function(res, a) {
                if(res.status == 403){
                    toastr.warning("Session expired.");
                    setTimeout(function(){
                        window.location = '/'
                    },5000)
                }else if (res.status == 400 || res.status == 500){
                    toastr.error(res.data.message);
                }
                return res;
            }
        };
    });
}

angular
    .module('iaasusage')
    .config(config)
    .config(HttpErrorInterceptor)
    .run(function($rootScope, $state) {
        $rootScope.$state = $state;
    });
