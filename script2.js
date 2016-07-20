$(document).ready(function(){

	// Generate session ID
	var SESSION_ID = "";
    var charset = "abcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 12; i++ )
        SESSION_ID += charset.charAt(Math.floor(Math.random() * charset.length));


    // Chatbox functionality
	$('.chat_head').click(function(){
		$('.chat_body').slideToggle('slow');
	});
	$('.msg_head').click(function(){
		$('.message_wrap').slideToggle('slow');
	});
	
	$('.close').click(function(){
		$('.module').hide();
	});
	
	$('.user').click(function(){

		$('.message_wrap').show();
		$('.msg_box').show();
	});
	
	// Handle button presses
	document.getElementById("ts_button").onclick = function () {
		// Prepare the API JSON call
		var apigClient = apigClientFactory.newClient();
		var params = {};
		var body = {
			"session_id": SESSION_ID,
		    "input": "TS_BUTTON_PRESS"
		};
		var additionalParams = {
		    headers: {
		    	"Content-Type": "application/json"
		    }
		};

		// Handle the API callback
		apigClient.conversationPost(params, body, additionalParams)
		    .then(function(result){
		        //This is where you would put a success callback
		        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
		        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
		    }).catch( function(result){
		        //This is where you would put an error callback
		        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
		        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
		    });

		// Ensures that chat window is fully scrolled down
		$('.message_area').scrollTop($('.message_area')[0].scrollHeight);; 
	};

	document.getElementById("nh_button").onclick = function () {

		// New Hire intro message
		$('<li class="other"><div class="messages">Alright, let\'s get started...</div></li>').insertBefore('.msg_push');
		$('.message_area').scrollTop($('.message_area')[0].scrollHeight);

		// Prepare the API JSON call
		var apigClient = apigClientFactory.newClient();
		var params = {};
		var body = {
			"session_id": SESSION_ID,
		    "input": "NH_BUTTON_PRESS"
		};
		var additionalParams = {
		    headers: {
		    	"Content-Type": "application/json"
		    }
		};

		// Handle the API callback
		apigClient.conversationPost(params, body, additionalParams)
		    .then(function(result){
		        //This is where you would put a success callback
		        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
		        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
		    }).catch( function(result){
		        //This is where you would put an error callback
		        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
		        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
		    });

		// Ensures that chat window is fully scrolled down
		$('.message_area').scrollTop($('.message_area')[0].scrollHeight);;
	};

	// Handle the message sending/receiving
	$('textarea').keypress(
    function(e){
        if (e.keyCode == 13) {
            e.preventDefault();
            var msg = $(this).val();
			$(this).val('');
			if(msg!=''){
				$('<li class="self"><div class="messages">' + msg + '</div></li>').insertBefore('.msg_push');

				// Prepare the API JSON call
				var apigClient = apigClientFactory.newClient();
				var params = {};
				var body = {
					"session_id": SESSION_ID,
				    "input": "" + msg
				};
				var additionalParams = {
				    headers: {
				    	"Content-Type": "application/json"
				    }
				};

				// Handle the API callback
				apigClient.conversationPost(params, body, additionalParams)
				    .then(function(result){
				        //This is where you would put a success callback
				        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
				        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
				    }).catch( function(result){
				        //This is where you would put an error callback
				        $('<li class="other"><div class="messages">' + result.data.message + '</div></li>').insertBefore('.msg_push');
				        $('.message_area').scrollTop($('.message_area')[0].scrollHeight);
				    });

				// Ensures that chat window is fully scrolled down
				$('.message_area').scrollTop($('.message_area')[0].scrollHeight);
			}
        }
    });
	
});