var APP_ID = '215062';
// var CHANNEL_URL = '/player/channel.html';
var CALLBACK = '/player/channel.html'

app.controller("indexController", function($http, $scope, $location) {
    $scope.types = [];
    $scope.tags = [];
    $scope.artists = [];
    $scope.albums = [];
    $scope.deezer = {};
    $scope.last = null;
    var already_loaded = false;
    
    var callback = window.location.protocol + '//' + window.location.host + CALLBACK;
    
    DZ.init({
      appId: APP_ID,
      channelUrl: encodeURIComponent(callback),
      player: {
        container:'player',
        onload: function () { 
        }
      }
    });
    
    
    $scope.login = function() {
      console.log('login clicked');
      
      DZ.login(function(response) {
        if (response.authResponse) {
          $('#deezer_login').hide();
          DZ.api('/user/me', function(response){
            $scope.deezer.username = response.name;
          });
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
    
    $scope.deezer_play = function(item) {
      console.log("playing")
      console.log(item);
      DZ.player.playRadio(item.id, 'artist');
    }
    
    $scope.update_deezer = function () {
      $http.get('/deezer.json').then(response => {
        var last = response.data;
        var play = false;
        if(!("last" in $scope.deezer)) {
          if(last.id != '') {
            play = true;
          }
        } else {
          if((last.type != $scope.deezer.last.type || last.id != $scope.deezer.last.id ) && last.id != '' ) {
            play = true;
          }
        }
        
        if(play) {
          $scope.deezer_play(last);
        }
        $scope.deezer.last = last;
        setTimeout($scope.update_deezer, 1000)
      }, function errorCallback(response) {
        console.log(response)
        setTimeout($scope.update_deezer, 1000)
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
      ids = []
      DZ.api('/search?q=' + encodeURIComponent(query), function(response){
        for(a in response.data) {
          artist = response.data[a];
          console.log(ids);
          console.log(artist.artist.id)
          console.log(jQuery.inArray(artist.artist.id, ids));
          if( jQuery.inArray(artist.artist.id, ids) == -1) {
            console.log(artist.artist.id + artist.artist.name + artist.artist.picture_small )
            $scope.artists.push({
              artist: artist.artist.name,
              artistid: artist.artist.id,
              thumbnail: artist.artist.picture_small
            });
            ids.push(artist.artist.id);
          }
        }
        console.log(response.data);
      });
    }
    
    setTimeout($scope.update_last, 1000)
    setTimeout($scope.update_deezer, 1000)
    
    
});
