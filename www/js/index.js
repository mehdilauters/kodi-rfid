app.controller("indexController", function($http, $scope, $location) {
    $scope.types = [];
    $scope.tags = [];
    
    $http.get('/types.json').then(response => {
        $scope.types = response.data;
    }, function errorCallback(response) {
    });
    
    $scope.select_type = function (type) {
        $http.get('/tags.json?type='+type).then(response => {
            $scope.tags = response.data;
        }, function errorCallback(response) {
        });
    }
    
    $scope.delete = function (tag) {
        $http.post("/delete.json", tag, {})
        .then(
            function(response){
                $("#tag_"+tag).hide();
            }, 
            function(response){
                // failure callback
            }
        );
    }
    
    
});
