$(document).ready(function(){
    $('.bet-header').click(function(){
        if($(this).hasClass("checked") == false){
            $(".checked").removeClass("checked");
        }
        this.classList.toggle('checked');
    });
});