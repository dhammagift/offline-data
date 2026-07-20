
      //Пути к директориям
      var pathToScript = '/Index/Scripts/';
      var pathToArticles = '/Teaching/Glossary/';
      //-----------------------------------
      var request = false;
      try {
          request = new XMLHttpRequest();
      } 
      catch (trymicrosoft) {
          try {
              request = new ActiveXObject("Msxml2.XMLHTTP");
          } 
          catch (othermicrosoft) {
              try {
                  request = new ActiveXObject("Microsoft.XMLHTTP");
              } 
              catch (failed) {
                  request = false;
              }  
          }
      }
 
      if (!request) {
          alert("Ошибка в работе");
      }  
 
      function sendRequest() {
          var url = "/Index/Scripts/build_array.php?scr="+pathToScript+"&art="+pathToArticles;
          request.open("GET", url, true);
          request.onreadystatechange = getResponse;
          request.send(null);
      }
 
      function getResponse() {
          if (request.readyState == 4) {
    	      if (request.status == 200) {
    	          var response = request.responseText;
    	          var articles = request.responseText.split(' ');
    	          var random = Math.round((Math.random()*(articles.length-2)));
    	          window.open("http://" + document.domain + articles[random], "_self");
    	      }    	       
    	  }
      }
