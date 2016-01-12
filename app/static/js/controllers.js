/**
 * INSPINIA - Responsive Admin Theme
 *
 */

/**
 * MainCtrl - controller
 */
function MainCtrl($http) {
	var mainCtrl = this
    this.userName = 'Example user';
    this.helloText = 'Welcome in SeedProject';
    this.descriptionText = 'It is an application skeleton for a typical AngularJS web app. You can use it to quickly bootstrap your angular webapp projects and dev environment for these projects.';

	this.countVmsByProject = function() {
    	$http.get('/api/v1/lab/project/?account_name=timeevolucaoinfra&domain_id=28f40084-2aed-11e5-8fce-76b2dd27c282')
    	.success(function(response) {
    		mainCtrl.countVmsByProject = response
    	})
    }
};

angular
    .module('iaasusage')
    .controller('MainCtrl', MainCtrl)