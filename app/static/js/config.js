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
    $urlRouterProvider.otherwise('/ebt/instances/projects');

    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });

    $stateProvider
        .state('index', {
            abstract: true,
            url: '',
            templateUrl: viewPrefix + 'common/content.html'
        })
        .state('index.instances', {
            url: '/:region/instances/:projectName/:projectId',
            templateUrl: viewPrefix + 'instances/vm_count.html',
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.instances_projects', {
            url: '/:region/instances/projects',
            templateUrl: viewPrefix + 'projects/list.html',
            data:{
                context: 'Instances',
                link: 'index.instances({projectName: projectCtrl.getProjectName(project), projectId: project.id, region: region.key})'
            },
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.storage_projects', {
            url: '/:region/storage/projects',
            templateUrl: viewPrefix + 'projects/list.html',
            data:{
                context: 'Storage',
                link: 'index.storage({projectName: projectCtrl.getProjectName(project), projectId: project.id, region: region.key})'
            },
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.storage', {
            url: '/:region/storage/:projectName/:projectId',
            templateUrl: viewPrefix + 'storage/list.html',
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.usage', {
            url: '/:region/usage/',
            templateUrl: viewPrefix + 'usage_record/list.html',
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.capacity', {
            url: '/:region/capacity/',
            templateUrl: viewPrefix + 'capacity/list.html',
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.quota_projects', {
            url: '/:region/quota/projects',
            templateUrl: viewPrefix + 'projects/list.html',
            data:{
                context: 'Resource Quota',
                link: 'index.quota({projectName: projectCtrl.getProjectName(project), projectId: project.id, region: region.key})'
            },
            resolve: {
                loadPlugin: loadPlugins
            }
        })
        .state('index.quota', {
            url: '/:region/quota/:projectName/:projectId',
            templateUrl: viewPrefix + 'quota/list.html',
            resolve: {
                loadPlugin: loadPlugins
            }
        })
}

function loadPlugins($ocLazyLoad) {
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
        },
        {
            serie: true,
            name: 'datatables.responsive',
            files: [staticPrefix + 'js/plugins/dataTables/dataTables.responsive.js',
                    staticPrefix + 'css/plugins/dataTables/dataTables.responsive.css']
        },
        {
            files: [staticPrefix + 'js/plugins/chartJs/Chart.min.js']
        },
        {
            name: 'tc-chartjs',
            files: [staticPrefix + 'js/plugins/chartJs/tc-angular-chartjs.js']
        },
        {
            name: 'moment',
            files: [staticPrefix + 'js/plugins/moment/moment.min.js']
        },
        {
            name: 'arrive',
            files: [staticPrefix + 'js/plugins/arrive/arrive.js']
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

function byteFilter() {
    return function(bytes, precision) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
        if (typeof precision === 'undefined') precision = 1;
        var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
            number = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision);
    }
}


function dateRageFilter(object, start_date, end_date){
    var result = [];

    // date filters
    var start_date = (start_date && !isNaN(Date.parse(start_date))) ? Date.parse(start_date) : 0;
    var end_date = (end_date && !isNaN(Date.parse(end_date))) ? Date.parse(end_date) : new Date().getTime();

    // if the conversations are loaded
    if (conversations && conversations.length > 0){
        $.each(conversations, function (index, conversation){
            var conversationDate = new Date(conversation.date_posted);

            if (conversationDate >= start_date && conversationDate <= end_date){
                result.push(conversation);
            }
        });

        return result;
    }
};


angular
    .module('iaasusage')
    .config(config)
    .config(HttpErrorInterceptor)
    .filter('byte', byteFilter)
    .run(function($rootScope, $state) {
        $rootScope.$state = $state;
    });
