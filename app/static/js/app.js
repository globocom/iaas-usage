(function () {
    var app = angular.module('iaasusage', [
        'ui.router',                    // Routing
        'oc.lazyLoad',                  // ocLazyLoad
        'ui.bootstrap',                 // Ui Bootstrap
    ])
    app.config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
    }]).run(function($rootScope, $window, $location){
        if($window.ga){
            if($location.host() == 'iaas-usage.globoi.com'){
                $window.ga('create', 'UA-77868670-1', 'auto');
            }else{
                $window.ga('create', 'UA-77868670-2', 'auto');
            }

            $rootScope.$on('$stateChangeSuccess', function (event) {
                $window.ga('send', 'pageview', $location.path());
            });
        }
    });
})();

