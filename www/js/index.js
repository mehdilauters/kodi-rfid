app.controller("indexController", function($http, $scope, $location) {
    $scope.types = [];
    $scope.tags = [];
    
    $scope.last = null;
    var already_loaded = false;
    
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
                console.log(response)
            }
        );
    }
    
    $scope.register = function (tag) {
        if($scope.last != null) {
            $('#register_container').show();
        }
        if( ! already_loaded ) {
            already_loaded = true;
            $http.get('/albums.json').then(response => {
                $scope.albums = response.data;
            }, function errorCallback(response) {
                console.log(response)
            });
            
            $http.get('/artists.json').then(response => {
                $scope.artists = response.data;
            }, function errorCallback(response) {
                console.log(response)
            });
            
            $http.get('/actions.json').then(response => {
                $scope.actions = response.data;
            }, function errorCallback(response) {
                console.log(response)
            });
            
            $http.get('/addons.json').then(response => {
                $scope.addons = response.data;
            }, function errorCallback(response) {
                console.log(response)
            });
        }
    }
    
    $scope.register_type_update = function () {
        $(".register_type_container").hide();
        $("#register_"+$scope.type).show();
    }
    
    $scope.update_last = function () {
        $http.get('/last.json').then(response => {
            var last = response.data.id;
            
            if(last != $scope.last) {
                $('#register_container').hide();
            }
            
            $scope.last = last;
            setTimeout($scope.update_last, 1000)
        }, function errorCallback(response) {
            console.log(response)
            setTimeout($scope.update_last, 1000)
        });
    }
    
    $scope.select_command = function(tag, command) {
        var data = $.param({
            command: command,
            tagid: tag
        });
        $http.post("/register.json", data, {})
        .then(
            function(response){
                $('#register_container').hide();
            }, 
            function(response){
                console.log(response)
            }
        );        
    }
    
    $scope.select_action = function(tag, action) {
        var data = $.param({
            action: action,
            tagid: tag
        });
        console.log(action)
        $http.post("/register.json", data, {})
        .then(
            function(response){
                $('#register_container').hide();
            }, 
            function(response){
                console.log(response)
            }
        );        
    }
    
    $scope.select_url = function(tag, url) {
        var data = $.param({
            url: url,
            tagid: tag
        });
        $http.post("/register.json", data, {})
        .then(
            function(response){
                $('#register_container').hide();
            }, 
            function(response){
                console.log(response)
            }
        );        
    }
    
    $scope.select_artist = function(tag, artistid) {
        var data = $.param({
            artistid: artistid,
            tagid: tag
        });
        $http.post("/register.json", data, {})
        .then(
            function(response){
                $('#register_container').hide();
            }, 
            function(response){
                console.log(response)
            }
        );        
    }
    
    $scope.select_album = function(tag, albumid) {
        var data = $.param({
            albumid: albumid,
            tagid: tag
        });
        $http.post("/register.json", data, {})
        .then(
            function(response){
                $('#register_container').hide();
            }, 
            function(response){
                console.log(response)
            }
        );        
    }
    
    $scope.register_addon_update = function () {
        $(".register_addon_container").hide();
        var elt = "#register_"+$scope.registered_addon.replace(/\./g,'_')+"_container";
        $(elt).show();
    }
    
    $scope.select_youtube = function(tag, addon, playlist, video) {
      var data = $.param({
        addon: addon,
        playlist: playlist,
        video: video,
        tagid: tag
      });
      $http.post("/register.json", data, {})
      .then(
        function(response){
          $('#register_container').hide();
        }, 
        function(response){
          console.log(response)
        }
      );         
    }
    
    setTimeout($scope.update_last, 1000)
    
    
});
