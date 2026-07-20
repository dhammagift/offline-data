		$(document).ready(function(){
		    
		    $(".buttons").click(function () {
		    var divname= this.value;
		      $("#"+divname).show("slow").siblings().hide("slow");
		    });
		
		  });