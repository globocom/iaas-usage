function RegionCtrl(regionService, $rootScope, $scope){

    regionCtrl = this
    regionCtrl.regionList = regionService.listRegions()
    regionCtrl.currentRegion = regionService.getCurrentRegion()

    regionCtrl.listRegions = function(){
        return regionCtrl.regionList
    }

    regionCtrl.changeRegion = function(region){
        if(region.key != regionService.getCurrentRegion().key){
            regionService.changeCurrentRegion(region)
            $rootScope.$broadcast('regionChanged')
        }
    }

    regionCtrl.toggleSelector = function(){
        regionCtrl.selectorClass = angular.isUndefined(regionCtrl.selectorClass) ? 'sidebar-open' : undefined
    }

    regionCtrl.getCurrentRegion = function(){
        return regionService.getCurrentRegion()
    }

    $scope.$on('regionChanged', function(){
        regionCtrl.toggleSelector()
    })
}

function UserCtrl($scope, $http, $state, userService) {

    userCtrl = this;
    userCtrl.user = null;

    userCtrl.loadUser = function(callback) {
        console.log('Loading user')

        userService.getCurrentUser(function(user){
            userCtrl.user = user
            if(angular.isDefined(callback)){
                callback()
            }
            $scope.$broadcast('userLoaded', userCtrl.user);
        })
    }

    $scope.$on('regionChanged', function(){
        userCtrl.loadUser(function(){
            $state.go('index.instances_projects');
        })
    })
};

function InstanceCtrl($scope, $http, $stateParams, $filter, apiService, listFilterService, tagService, DTOptionsBuilder){

    instanceCtrl = this
    instanceCtrl.title = 'Instances';
    instanceCtrl.projectName = '';
    instanceCtrl.vmCount
    instanceCtrl.instances = []
    instanceCtrl.instanceView = []
    instanceCtrl.filters = {}
    instanceCtrl.tags = []

    $scope.dtOptions = DTOptionsBuilder.newOptions()
    .withDOM('<"html5buttons"B>lTfgitp')
    .withOption('responsive', true)
    .withButtons([{extend: 'copy'}, {extend: 'csv'}]);

    instanceCtrl.getInstances = function(){
        return instanceCtrl.instanceView
    }

    instanceCtrl.getVmCountByFeature = function(feature){
        if(angular.isDefined(instanceCtrl.vmCount)){
            return instanceCtrl.vmCount[feature]
        }
    }

    instanceCtrl.listVirtualMachines = function(){
        console.log('Loading virtual machines')

        instanceCtrl.projectName = decodeURIComponent($stateParams.projectName)
        var params = $.extend({project_id: $stateParams.projectId}, tagService.buildTagParams(instanceCtrl.tags))

        $http({
            method: 'GET',
            url: apiService.buildAPIUrl('/virtual_machine/', params)
        }).then(function successCallback(response){
            instanceCtrl.instances = response.data.vms.virtual_machines;
            instanceCtrl.instanceView = instanceCtrl.instances;

            instanceCtrl.vmCount = {}
            angular.forEach(response.data.summary, function(values, featureName) {
                var _this = []
                angular.forEach(response.data.summary[featureName], function(value, key) {
                    _this.push({name: key, count: value});
                });
                instanceCtrl.vmCount[featureName] = _this
            });

            if(instanceCtrl.instances.length == 0){
                toastr.warning("No virtual machines were found for selected filter.");
            }
        });
    }

    instanceCtrl.filter = function(label,field, value){
        console.log('Filter virtual machine list. field: ' + field + ' value: ' + value)
        if(instanceCtrl.filters[field] != value){
            toastr.success("Filtering instances by " + label + ".");
        }else{
            toastr.success(label + " filter removed.");
        }

        instanceCtrl.instanceView = listFilterService.filter(instanceCtrl.instances, instanceCtrl.filters, field, value)
    }

    instanceCtrl.clearFilters = function(){
        toastr.success("Removing filters")
        instanceCtrl.filters = {}
        if(instanceCtrl.tags.length > 0){
            instanceCtrl.tags = []
            instanceCtrl.listVirtualMachines()
        }else{
            instanceCtrl.instanceView = listFilterService.filter(instanceCtrl.instances, instanceCtrl.filters, null, null)
        }
    }

    instanceCtrl.isFilteredField = function(field, value){
        return instanceCtrl.filters[field] == value
    }

    instanceCtrl.filterByTag = function(key, value){
        if(key && value){
            instanceCtrl.tags.push({key: key, value: value})
            instanceCtrl.tagKey = null;
            instanceCtrl.tagValue = null;
            instanceCtrl.filters = {}
            instanceCtrl.listVirtualMachines()
        }
    }

    instanceCtrl.removeTagFilter = function(key, value){
        for(var i = 0 ; i < instanceCtrl.tags.length ; i++){
            if(instanceCtrl.tags[i].key == key && instanceCtrl.tags[i].value == value){
                instanceCtrl.tags.splice(i, 1);
            }
        }
        instanceCtrl.listVirtualMachines()
    }
}

function StorageCtrl($scope, $http, $stateParams, $filter, apiService, listFilterService, tagService, resourceLimitService, DTOptionsBuilder){

    storageCtrl = this
    storageCtrl.title = 'Storage';
    storageCtrl.projectName = '';
    storageCtrl.storage = []
    storageCtrl.storageView = []
    storageCtrl.filters = []
    storageCtrl.tags = []

    $scope.dtOptions = DTOptionsBuilder.newOptions()
    .withDOM('<"html5buttons"B>lTfgitp')
    .withOption('responsive', true)
    .withButtons([{extend: 'copy'}, {extend: 'csv'}]);

    storageCtrl.getStorage = function(){
        return storageCtrl.storageView
    }

    storageCtrl.getSnapshots = function(){
        return $filter('filter')(storageCtrl.storage, {storage_type: 'Snapshot'})
    }

    storageCtrl.getVolumes = function(){
        return $filter('filter')(storageCtrl.storage, {storage_type: 'Volume'})
    }

    storageCtrl.listStorage = function(){
        console.log('Loading storage')

        storageCtrl.projectName = decodeURIComponent($stateParams.projectName)
        var params = $.extend({project_id: $stateParams.projectId}, tagService.buildTagParams(storageCtrl.tags))

        $http({
            method: 'GET',
            url: apiService.buildAPIUrl('/storage/', params)
        }).then(function successCallback(response){
            storageCtrl.storage = response.data.storage;
            storageCtrl.storageView = storageCtrl.storage;

            if(storageCtrl.storage.length == 0){
                toastr.warning("Nothing was found for selected filter.");
            }
        });
    }

    storageCtrl.filter = function(field, value, data){
        console.log('Filter storage list. field: ' + field)

        toastr.success("Filtering storages by " + data[0].label + ".");

        $scope.$apply(function(){
            storageCtrl.filters = {}
            if(field == 'created_at'){
                if(data[0].label == "Older than 1 month"){
                    storageCtrl.storageView = storageCtrl.oneMonthSnapshots
                }else if(data[0].label == "Older than 3 months"){
                    storageCtrl.storageView = storageCtrl.threeMonthSnapshots
                }else if(data[0].label == "Older than one year"){
                    storageCtrl.storageView = storageCtrl.oneYearSnapshots
                }
                return;
            }

            if(angular.isDefined(data)){
                if(data[0].label == 'Attached Volumes'){
                    value = true
                }
                if(data[0].label == 'Detached Volumes'){
                    value = false
                }
            }

            storageCtrl.storageView = listFilterService.filter(storageCtrl.storage, storageCtrl.filters, field, value)
        });
    }

    storageCtrl.clearFilters = function(){
        toastr.success("Removing filters")
        storageCtrl.filters = []
        if(storageCtrl.tags.length > 0){
            storageCtrl.tags = []
            storageCtrl.listStorage()
        }else{
            storageCtrl.storageView = listFilterService.filter(storageCtrl.storage, storageCtrl.filters, null, null)
        }
    }

    storageCtrl.filterByTag = function(key, value){
        if(key && value){
            storageCtrl.tags.push({key: key, value: value})
            storageCtrl.tagKey = null;
            storageCtrl.tagValue = null;
            storageCtrl.listStorage()
        }
    }

    storageCtrl.removeTagFilter = function(key, value){
        for(var i = 0 ; i < storageCtrl.tags.length ; i++){
            if(storageCtrl.tags[i].key == key && storageCtrl.tags[i].value == value){
                storageCtrl.tags.splice(i, 1);
            }
        }
        storageCtrl.listStorage()
    }

    $scope.$watch('storageCtrl.storage', function(newValue, oldValue){
        if(newValue != oldValue && storageCtrl.storage.length > 0){
            storageCtrl.buildGraphData()
        }
    });

    storageCtrl.getStorageByDateBetween = function(start, end){
        return $.grep(storageCtrl.getSnapshots(), function(snapshot) {
            var snapshotDate = moment(snapshot.created_at, moment.ISO_8601);

            if(angular.isDefined(start) && angular.isDefined(end)){
                return snapshotDate.isBetween(moment().subtract(end.count, end.unit), moment().subtract(start.count, start.unit));
            }else{
                return snapshotDate.isBefore(moment().subtract(start.count, start.unit))
            }
        });
    }

    storageCtrl.buildGraphData = function(){
        resourceLimitService.getResourceLimits($stateParams.projectId, function(project){

            var volumes = storageCtrl.getVolumes()
            var volumeUsed = storageCtrl._sum(volumes, 'size') / (1024 * 1024 * 1024)
            // volume limit GB
            storageCtrl.graph1 = [
                {
                    value: project.primary_storage_limit - volumeUsed,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Volumes available (GB)"
                },
                {
                    value: volumeUsed,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Volumes used (GB)"
                }
            ];

            // volume limit units
            storageCtrl.graph2 = [
                {
                    value: project.volume_limit - volumes.length,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Volumes available (unit)"
                },
                {
                    value: volumes.length,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Volumes used (unit)"
                }
            ];

            // volume detached x attached
            storageCtrl.graph3 = [
                {
                    value: $filter('filter')(volumes, {attached: true}).length,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Attached Volumes"
                },
                {
                    value: $filter('filter')(volumes, {attached: false}).length,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Detached Volumes"
                }
            ];

            var snapshots = storageCtrl.getSnapshots()
            var snapshotsUsed = storageCtrl._sum(snapshots, 'size') / (1024 * 1024 * 1024)

            // snapshot limit GB
            storageCtrl.graph4 = [
                {
                    value: project.sec_storage_limit - snapshotsUsed,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Snapshots available (GB)"
                },
                {
                    value: snapshotsUsed,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Snapshots used (GB)"
                }
            ];

            // snapshot limit units
            storageCtrl.graph5 = [
                {
                    value: project.snapshot_limit - project.snapshot_used,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Snapshots available (unit)"
                },
                {
                    value: project.snapshot_used,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Snapshots used (unit)"
                }
            ];

            storageCtrl.oneMonthSnapshots = storageCtrl.getStorageByDateBetween({count:1, unit: 'month'}, {count:3, unit: 'month'})
            storageCtrl.threeMonthSnapshots = storageCtrl.getStorageByDateBetween({count:3, unit: 'month'}, {count:1, unit: 'year'})
            storageCtrl.oneYearSnapshots = storageCtrl.getStorageByDateBetween({count: 1, unit: 'year'})

            //snapshot age
            storageCtrl.graph6 = [
                {
                    value: storageCtrl.oneMonthSnapshots.length,
                    color:"#54697E",
                    highlight: "#8F9396",
                    label: "Older than 1 month"
                },
                {
                    value: storageCtrl.threeMonthSnapshots.length,
                    color: "#FFA500",
                    highlight: "#FF8800",
                    label: "Older than 3 months"
                },
                {
                    value: storageCtrl.oneYearSnapshots.length,
                    color:"#FF3700",
                    highlight: "#FC7C58",
                    label: "Older than one year"
                }
            ];

            storageCtrl.doughnutOptions = {
                segmentShowStroke : true,
                segmentStrokeColor : "#fff",
                segmentStrokeWidth : 2,
                percentageInnerCutout : 45, // This is 0 for Pie charts
                animationSteps : 100,
                animationEasing : "easeOutBounce",
                animateRotate : true,
                animateScale : false,
                responsive: true,
            };
        });
    }

    storageCtrl._sum = function(items, prop){
        return items.reduce( function(a, b){
            return a + b[prop];
        }, 0);
    };
}


function UsageCtrl($scope, $http, $stateParams, userService, apiService, DTOptionsBuilder){

    usageCtrl = this
    usageCtrl.title = 'Resource usage';
    usageCtrl.records = []
    usageCtrl.recordsView = []

    $scope.dtOptions = DTOptionsBuilder.newOptions()
    .withDOM('<"html5buttons"B>lTfgitp')
    .withOption('responsive', true)
    .withButtons([{extend: 'copy'}, {extend: 'csv'}, {extend: 'print'}]);

    usageCtrl.listUsageRecords = function(start, end) {
        if(angular.isUndefined(start)){
            start = moment().subtract(1, 'months').format('YYYY-MM-DD')
        }
        if(angular.isUndefined(end)){
            end = moment().subtract(1, 'days').format('YYYY-MM-DD')
        }

        userService.getCurrentUser(function(user){
            var params = {start_date: start, end_date: end}
            if(!user.is_admin){
                params.account_name = user.account_name
            }

            $http({
                method: 'GET',
                url: apiService.buildAPIUrl('/usage_record/', params)
            }).then(function successCallback(response){
                usageCtrl.records = response.data.usage;
                usageCtrl.recordsView = usageCtrl.usage;
                if(usageCtrl.records.length == 0){
                    toastr.warning("No usage data was found on the selected date range.");
                }
            });
        })
    }

    usageCtrl.getRecords = function(){
        return usageCtrl.records;
    }
}

function ProjectCtrl($scope, $http, $state, apiService, DTOptionsBuilder){

    projectCtrl = this
    projectCtrl.projects
    projectCtrl.context = $state.current.data.context
    projectCtrl.link = $state.current.data.link

    $scope.dtOptions = DTOptionsBuilder.newOptions()
        .withOption('responsive', true)
        .withOption('aaSorting', [[1, 'desc']]);

    projectCtrl.listProjects = function(event, user) {
        user = user || userCtrl.user
        if(angular.isUndefined(this.projects) && user != null){
            console.log('Loading projects')

            $http({
                method: 'GET',
                url: apiService.buildAPIUrl('/project/', {account_name: user.account_name, domain_id: user.domain_id, is_admin: user.is_admin})
            }).then(function successCallback(response){
                projectCtrl.projects = response.data;
            });
        }
    }

    projectCtrl.getProjectName = function(project){
        return encodeURIComponent(project.name)
    }

    $scope.$on('userLoaded', projectCtrl.listProjects)
}

angular
    .module('iaasusage')
    .controller('RegionCtrl', RegionCtrl)
    .controller('UserCtrl', UserCtrl)
    .controller('ProjectCtrl', ProjectCtrl)
    .controller('InstanceCtrl', InstanceCtrl)
    .controller('UsageCtrl', UsageCtrl)
    .controller('StorageCtrl', StorageCtrl);