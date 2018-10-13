$(document).ready(function(){

    var connection_string = document.getElementsByTagName('body')[0].getAttribute('id');
    console.log('Trying to connect to ' + connection_string);

    var socket = io.connect(connection_string);

    socket.on('connect', function(){
        console.log('Connected to the server');
        socket.emit('client_connected', {username: 'Some username'});
    });

    socket.on('new_client', function(){
        console.log('new client has connected');
    });
    socket.on('run_script', function(data){
        $('#js-btn-jump').text('Rolling...')
        $(document).trigger('data-run-script', data);
        if(isUserLoggedIn()){
            updateBalance();
        }
    });
    socket.on('update_time', function(data){
        $('#js-btn-jump').text('Time left: ' + data + 's')
    });
    $('#bet-button').click(function(){
        if (document.getElementsByClassName('checked').length > 0){
            if(isNaN($('#bet-amount').val()) == false){
                if(isUserLoggedIn()){
                    var bet_amount = Number($('#bet-amount').val());
                    var user_identifier = getCookie('user_identifier');
                    var alternative = document.getElementsByClassName('checked')[0].getAttribute('data-value');

                    var json_data = {
                        'bet_amount': bet_amount,
                        'user_identifier': user_identifier,
                        'alternative': alternative
                    };

                    socket.emit('client_bet', json_data);

                }
                else{
                    swal('Login to place bets');
                }
            }
            else{
                swal('Enter a valid bet amount');
            }
        }
        else{
            swal('Select a color')
        }
    });

    socket.on('bet_response', function(data){
        var json_obj = $.parseJSON(data);
        if(json_obj['status'] == 'fail'){
            swal(json_obj['message']);
        }
        else{
            updateBalance();
        }

    });

    socket.on('update_user_response', function(data){
        $('#balance').text('Balance ' + data);
    });

    socket.on('new_bet', function(data){
        var json_obj = $.parseJSON(data);
        $('#' + json_obj['alternative'] + '-table').append('<tr><td>' + json_obj['name'] + '</td><td>' + json_obj['amount'] + '$</td><tr>');
    });

    socket.on('login_required', function(){
        console.log('Login required')
        window.location.replace('/login');
    });

    socket.on('error', function(data){
        swal(data);
    });

    function isUserLoggedIn(){
        var match = document.cookie.match(new RegExp('(^| )' + 'user_identifier' + '=([^;]+)'));
        if (match){
            return true;
        }
    }

    function getCookie(name){
        var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        if (match) return match[2];
    }
    function updateBalance(){
        socket.emit('update_user', {'identifier': getCookie('user_identifier')});
    }
});