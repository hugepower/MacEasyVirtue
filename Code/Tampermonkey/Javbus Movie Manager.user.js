// ==UserScript==
// @name Javbus Movie Manager
// @name:zh-CN Javbus 影片管理器
// @namespace http://tampermonkey.net/
// @version 1.1
// @description This plugin modifies the page to show your local movie files information, such as adding tags and playing them from the local source.
// @author hugepower
// @match https://www.javbus.com/*
// @icon https://www.google.com/s2/favicons?sz=64&domain=javbus.com
// @grant GM_xmlhttpRequest
// @grant GM_download
// @updateURL https://github.com/hugepower/MacEasyVirtue/raw/main/Code/Tampermonkey/Javbus%20Movie%20Manager.user.js
// ==/UserScript==

(function () {
  'use strict';

  // Send a request to the server and get the movie information
  function getMovieInfo() {
    GM_xmlhttpRequest({
      method: 'get',
      url: 'http://127.0.0.1:8082/javbus/',
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3887.7 Safari/537.36',
      },
      onload: function (responseDetails) {
        var movieInfo = JSON.parse(responseDetails.responseText);
        replaceDateTags(movieInfo);
      },
      onerror: function () {
        clearTimeout(timer);
        console.log('Stop the timeout');
      },
    });
  }

  // Replace the date tags with play buttons for downloaded movies
  function replaceDateTags(movieInfo) {
    var items = document.querySelectorAll('.photo-info');
    items.forEach(function (item) {
      var dateTag = item.querySelector('date');
      if (dateTag) {
        var movieId = dateTag.innerText;
        if (movieInfo[movieId]) {
          var playButton = createPlayButton(movieId);
          dateTag.parentNode.replaceChild(playButton, dateTag);
        }
      }
    });
    timer = setTimeout(replaceDateTags, 2000, movieInfo);
  }

  // Create a play button with the movie id and path
  function createPlayButton(movieId) {
    var playButton = document.createElement('a');
    playButton.setAttribute('class', 'btn btn-xs btn-primary');
    playButton.innerText = movieId;
    playButton.onmouseout = function () {
      playButton.innerText = movieId;
    };
    playButton.onmouseover = function () {
      playButton.innerText = 'Play Movie';
    };
    playButton.addEventListener('click', function (event) {
      // call the preventDefault method of the event object
      event.preventDefault();
      postMovieId(movieId);
    });
    return playButton;
  }

  // Post the movie id to another server when play button is clicked
  function postMovieId(movieId) {
    GM_xmlhttpRequest({
      method: 'POST',
      url: 'http://127.0.0.1:8082/javbus/post/',
      data: JSON.stringify({ movie_id: movieId }),
      headers: {
        'Content-Type': 'application/json',
      },
      onload: function (responseDetails) {
        console.log(responseDetails.responseText);
      },
      onerror: function (responseDetails) {
        console.log(responseDetails.responseText);
      },
    });
  }

  var timer;

  // check the active li element
  function checkActiveLi() {
    var text = document.querySelector('ul.nav.navbar-nav > li.active > a').innerText;
    if (text === '有碼') {
      getMovieInfo();
    }
  }

  window.addEventListener('load', checkActiveLi);
})();
