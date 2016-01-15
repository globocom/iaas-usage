/**
 * MainCtrl - controller
 */
function MainCtrl($http, $stateParams, $state) {
    var mainCtrl = this
    this.userName = 'Example user';
    this.helloText = 'Welcome in SeedProject';
    this.descriptionText = 'It is an application skeleton for a typical AngularJS web app. You can use it to quickly bootstrap your angular webapp projects and dev environment for these projects.';

    this.project = {name: $stateParams.projectName, id: $stateParams.projectId}

    this.countVmsByProject = function() {
        console.log('load vms count ...')
        $http.get('/api/v1/lab/project/?account_name=timeevolucaoinfra&domain_id=28f40084-2aed-11e5-8fce-76b2dd27c282')
        .success(function(response) {
            mainCtrl.countVmsByProject = response;
        })
    }

    this.loadProject = function() {
        console.log('load project... ');
        $http.get('/api/v1/lab/vm_count/?project_id=' + $stateParams.projectId)
        .success(function(response){
            mainCtrl.project = response;
        })
    }
    this.listVirtualMachines = function(){
        $http.get('/api/v1/lab/virtual_machine/?project_id=' + $stateParams.projectId)
        .success(function(response){
            mainCtrl.instances = response.virtual_machines;
        })
    }

    this.loadIndexInstanes = function() {
        console.log("loadings")
        $state.go('index.instances.index')
    }
};

function InstancesCtrl($http){

}

angular
    .module('iaasusage')
    .controller('MainCtrl', MainCtrl)
    .controller('InstancesCtrl', InstancesCtrl)