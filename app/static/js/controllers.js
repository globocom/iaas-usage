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
		console.log('load vms count ...')
    	$http.get('/api/v1/lab/project/?account_name=timeevolucaoinfra&domain_id=28f40084-2aed-11e5-8fce-76b2dd27c282')
    	.success(function(response) {
    		mainCtrl.countVmsByProject = response;
    	})
    }

    this.loadProject = function(projectId) {
    	console.log('load project... ');
    	console.log(projectId);
    	$http.get('/api/v1/lab/vm_count/?project_id=' + projectId)
    	.success(function(response){
    		mainCtrl.project = response;
    	})
    }
    this.listVirtualMachines = function(projectId){
    	console.log('load vms... ');
    	console.log(projectId);
    	$http.get('/api/v1/lab/virtual_machine/?project_id=' + projectId)
    	.success(function(response){
    		mainCtrl.instances = response.virtual_machines;
    	})
    }
};

angular
    .module('iaasusage')
    .controller('MainCtrl', MainCtrl)