//<![CDATA[
   $(document).ready(function(){
      $(".clicked1").click(
         function() {
            $(this).find("ul").slideToggle();
         }
      );
   });
//]]>