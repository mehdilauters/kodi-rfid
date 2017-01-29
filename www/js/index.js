var APP_ID = '215062';
var CALLBACK = '/'

app.controller("indexController", function($http, $scope, $location, $cookies, $cookieStore) {
    $scope.types = [];
    $scope.tags = [];
    $scope.artists = [];
    $scope.albums = [];
    $scope.deezer = {};
    $scope.last = null;
    $scope.deezer_mode = false;
    $scope.deezer_volume_step = 10;
    $scope.cookie = $cookieStore.get('serial');
    $scope.serial=$cookieStore.get('serial');
    
    if( $scope.serial === undefined ) {
      $scope.serial = ''
    }
    
    var tag_timeout = 1000;
    var deezer_timeout = 1000;
    
    var already_loaded = false;
    
    var callback = window.location.protocol + '//' + window.location.host + CALLBACK;
    
    var deezer_init = function() {
      DZ.init({
        appId: APP_ID,
        channelUrl: encodeURIComponent(callback),
              player: {
                container:'player',
              onload: function () { 
              }
              }
      });
      
      $scope.login();
    }
    
    var init = function() {
      
      $http.get('/types.json').then(response => {
        $scope.types = response.data;
      }, function errorCallback(response) {
      });
      
      $http.get('/mode.json').then(response => {
        mode = response.data;
        console.log(mode);
        if(mode == 'deezer') {
          $scope.deezer_mode = true;
          deezer_init();
        }
        
      }, function errorCallback(response) {
      }); 
    }
    
    $scope.save_serial = function() {
      var now = new Date(),
      // this will set the expiration to 12 months
      exp = new Date(now.getFullYear()+1, now.getMonth(), now.getDate());
      $cookies.putObject('serial',$scope.serial,{'expires':exp})
      
      $scope.cookie = $cookieStore.get('serial');
    }
    
    $scope.login = function() {
      console.log('login clicked');
      
      DZ.login(function(response) {
        if (response.authResponse.accessToken != null) {
          $scope.deezer.token = response.authResponse.accessToken;
          $('#deezer_login').hide();
          setTimeout($scope.update_deezer, deezer_timeout);
          DZ.api('/user/me', function(response){
            $scope.deezer.username = response.name;
            console.log($scope.deezer.username);
          });
          console.log('logged ' + $scope.deezer.token);
          $scope.logged();
          
        } else {
          console.log(response);
        }
      }, {scope: 'manage_library,basic_access'});
    };
    
    $scope.logged = function() {
      $scope.logged = true;
      console.log('Player loaded');
      $('#controls').css('opacity', 1);
//       $scope.handleRoute();
    };
    
    $scope.select_type = function (type) {
        $http.get('/tags.json?serial='+$scope.serial+'&type='+type).then(response => {
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
            
            
            angular.forEach($scope.types, function(t){
              $http.get('/'+t+'s.json').then(response => {
                console.log('$scope['+t + 's] = '+response.data);
                console.log($scope[t + 's']);
                if( response.data != null ) {
                  $scope[t + 's'] = response.data;
                } else {
                  $scope[t + 's'] = [];
                }
              }, function errorCallback(response) {
                console.log(response)
              }); 
            });
        }
    }
    
    $scope.register_type_update = function () {
        $(".register_type_container").hide();
        $("#register_"+$scope.type).show();
    }
    
    $scope.update_last = function () {
        $http.get('/last.json?serial='+$scope.serial).then(response => {
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
            setTimeout($scope.update_last, tag_timeout)
        }, function errorCallback(response) {
            console.log(response)
            setTimeout($scope.update_last, tag_timeout)
        });
    }
    
    $scope.deezer_play_pause = function() {
      if(DZ.player.isPlaying()) {
        DZ.player.pause();
      } else {
        DZ.player.play();
      }
    }
    
    $scope.deezer_action = function(item) {
      console.log(item);
      if(item.type == 'artist') {
        DZ.player.playRadio(item.id, 'artist');
      } else if(item.type == 'album') {
        DZ.player.playAlbum(item.id);
      } else if(item.type == 'action' && item.id == 'play_pause') {
        $scope.deezer_play_pause();
      } else if(item.type == 'action' && item.id == 'volume_down') {
        $scope.deezer_volume_down();
      } else if(item.type == 'action' && item.id == 'volume_up') {
        $scope.deezer_volume_up();
      } else if(item.type == 'action' && item.id == 'next') {
        $scope.deezer_next();
      }
    }
    
    $scope.deezer_next = function() {
      DZ.player.next();
    }
    
    $scope.deezer_volume_down = function(item) {
      console.log('down!');
      DZ.player.setVolume(DZ.player.getVolume() - $scope.deezer_volume_step);
    }
    
    $scope.deezer_volume_up = function(item) {
      console.log('up!');
      DZ.player.setVolume(DZ.player.getVolume() + $scope.deezer_volume_step);
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
          $scope.deezer_action(last);
        }
        $scope.deezer.last = last;
        setTimeout($scope.update_deezer, deezer_timeout)
      }, function errorCallback(response) {
        console.log(response)
        setTimeout($scope.update_deezer, deezer_timeout)
      });
    }
    
    $scope.select_command = function(tag, command) {
        var data = $.param({
            command: command,
            tagid: tag,
            serial: $scope.serial
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
            tagid: tag,
            serial: $scope.serial
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
            tagid: tag,
            serial: $scope.serial
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
            tagid: tag,
            serial: $scope.serial
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
            tagid: tag,
            serial: $scope.serial
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
        tagid: tag,
        serial: $scope.serial
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
    
    $scope.search_albums = function(query) {
      $scope.albums = [];
      ids = []
      DZ.api('/search?q=' + encodeURIComponent(query), function(response){
        for(a in response.data) {
          album = response.data[a];
          if( jQuery.inArray(album.album.id, ids) == -1) {
            console.log(album.album.id + album.album.name + album.album.cover_small )
            $scope.albums.push({
              title: album.album.name,
              artist: [album.artist.name],
              albumid: album.album.id,
              thumbnail: album.album.cover_medium
            });
            ids.push(album.album.id);
          }
        }
        console.log(response.data);
      });
    }
    
    $scope.search_artists = function(query) {
      $scope.artists = [];
      ids = [];
      DZ.api('/search?q=' + encodeURIComponent(query), function(response){
        for(a in response.data) {
          artist = response.data[a];
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
    
    init();
    $scope.update_last();
    
    
});
