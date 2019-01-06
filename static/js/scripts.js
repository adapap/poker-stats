
$(function(){

    $("#most-final-tables").click(function(){

        $("#final-tables").show().siblings("div").hide();


    });

     $("#most-top-3").click(function(){

        $("#top-3").show().siblings("div").hide();


    });

     $("#submitbutton").click(function(){

         var search = $("#searchbox");
         var input = search.val().length;


         if (input === 0){
             alert("Please make sure your search is at least 3 characters.")

         }else{
             document.location.href = "/search/" + search.val();
         }



    });


});