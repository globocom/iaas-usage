/**
 * INSPINIA - Responsive Admin Theme
 *
 */
(function () {
    var app = angular.module('iaasusage', [
        'ui.router',                    // Routing
        'oc.lazyLoad',                  // ocLazyLoad
        'ui.bootstrap',                 // Ui Bootstrap
    ])
    app.config(['$interpolateProvider', function($interpolateProvider) {
  		$interpolateProvider.startSymbol('{[');
  		$interpolateProvider.endSymbol(']}');
	}]);
})();

