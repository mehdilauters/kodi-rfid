var APP_ID = '215062';
var CHANNEL_URL = '/player/channel.html';

app.controller("indexController", function($http, $scope, $location) {
    $scope.types = [];
    $scope.tags = [];
    $scope.artists = [];
    $scope.albums = [];
    
    $scope.last = null;
    var already_loaded = false;
    
    DZ.init({
      appId: APP_ID,
      channelUrl: CHANNEL_URL,
      player: {
        onload: function () { 
        }
      }
    });
    
    
    $scope.login = function() {
      console.log('login clicked');
      
      DZ.login(function(response) {
        if (response.authResponse) {
          console.log('logged');
          $scope.logged();
        } else {
          console.log('not logged');
        }
      }, {scope: 'manage_library,basic_access'});
    };
    
    $scope.logged = function() {
      $scope.logged = true;
      console.log(LOGNS, 'Player loaded');
      $('#controls').css('opacity', 1);
//       $scope.handleRoute();
    };
    
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
        element = $('#register_container');
        if(element.is(":visible")) {
            element.hide();
        } else {
            if($scope.last != null) {
                element.show();
            }
        }
        if( ! already_loaded ) {
            already_loaded = true;
            for( t in $scope.types) {
              $http.get('/'+$scope.types[t]+'s.json').then(response => {
                $scope[$scope.types[t]] = response.data;
              }, function errorCallback(response) {
                  console.log(response)
              });
            }
        }
    }
    
    $scope.register_type_update = function () {
        $(".register_type_container").hide();
        $("#register_"+$scope.type).show();
    }
    
    $scope.update_last = function () {
        $http.get('/last.json').then(response => {
            var last = response.data.id;
            if(last == null) {
                $("#register_container_main").hide();
            } else {
                $("#register_container_main").show();
            }
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
    
    $scope.search_artists = function(query) {
      console.log(query);
      DZ.api('/search?q=' + query, function(response){
        console.log(response.data);
      });
    }
    
    setTimeout($scope.update_last, 1000)
    
    
});
