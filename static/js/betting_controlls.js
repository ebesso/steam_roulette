$(document).ready(function(){
    $('.dot').click(function(){
        if($(this).hasClass("checked") == false){
            $(".checked").removeClass("checked");
        }
        this.classList.toggle('checked');
    });
});