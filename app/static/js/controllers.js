/**
 * MainCtrl - controller
 */

var MainCtrl = function($http, $stateParams, $state, $q) {
    var mainCtrl = this;
    
    this.loadUser = function() {
        $http.get('/api/v1/lab/current_user/')
        .success(function(response){
            console.log(response)
            mainCtrl.user = response[0];
        })
    }
 
};

function InstanceCtrl($http, $stateParams, $state){
    var instanceCtrl = this
    this.title = 'Instances';
    this.mainCtrl;

    this.project = {name: $stateParams.projectName, id: $stateParams.projectId}
    
    this.load = function(mainCtrl) {
        console.log("loading InstancesCtrl: " + mainCtrl)
        console.log(mainCtrl)
        this.mainCtrl = mainCtrl;
        this.countVmsByProject();
    }

    this.countVmsByProject = function() {
        console.log('load vms count ...')
        $http.get('/api/v1/lab/project/?account_name='+ this.mainCtrl.user.account_name +'&domain_id=' + this.mainCtrl.user.domain_id)
        .success(function(response) {
            instanceCtrl.countVmsByProject = response;
        });
    }
    this.loadProject = function() {
        console.log('load project... ');
        $http.get('/api/v1/lab/vm_count/?project_id=' + $stateParams.projectId)
        .success(function(response){
            instanceCtrl.project = response;
        })
    }

    this.listVirtualMachines = function(){
        $http.get('/api/v1/lab/virtual_machine/?project_id=' + $stateParams.projectId)
        .success(function(response){
            instanceCtrl.instances = response.virtual_machines;
        })
    }

}

angular
    .module('iaasusage')
    .controller('MainCtrl', MainCtrl)
    .controller('InstanceCtrl', InstanceCtrl)