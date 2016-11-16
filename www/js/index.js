app.controller("indexController", function($http, $scope, $location) {
    $scope.types = [];
    $scope.tags = [];
    
    $http.get('/types.json').then(response => {
        $scope.types = response.data;
    }, function errorCallback(response) {
    });
    
    $http.get('/albums.json').then(response => {
        $scope.albums = response.data;
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
    
    $scope.register = function (tag) {
        $('#register_container').show();
    }
    
    $scope.register_type_update = function () {
        $(".register_type_container").hide();
        $("#register_"+$scope.type).show();
    }
    
    $scope.update_last = function () {
        $http.get('/last.json').then(response => {
            $scope.last = response.data.id;
            setTimeout($scope.update_last, 1000)
        }, function errorCallback(response) {
            console.log(response)
            setTimeout($scope.update_last, 1000)
        });
    }
    
    
    setTimeout($scope.update_last, 1000)
    
    
});
