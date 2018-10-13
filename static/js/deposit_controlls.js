$(document).ready(function(){
    var deposit_value = 0

    $('.img-container').click(function(){
        if($(this).hasClass("checked") == false){
            deposit_value = deposit_value + parseFloat($(this).attr('data-price'));
        }
        else{
            deposit_value = deposit_value - parseFloat($(this).attr('data-price'));
        }
        if (deposit_value < 0){
            deposit_value = 0
        }
        deposit_value = Math.round(deposit_value * 100) / 100

        document.getElementById('deposit-button').innerHTML = 'Deposit ' + deposit_value + '$';

        this.classList.toggle('checked');
        checkbox = document.getElementById(this.getAttribute('data-assetid'));

        if(checkbox.checked){
            checkbox.checked = false;
        }
        else{
            checkbox.checked = true;
        }
        console.log(checkbox.checked);
    });
    $('#deposit-button').click(function(){
        
        var checked_elements = document.getElementsByClassName('checked');
        
        if(checked_elements.length == 0){
            swal('Select some items to deposit');
        }
        else{
            document.getElementById('deposit-form').submit()
        }

    });
});