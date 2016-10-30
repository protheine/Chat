/**
 * Initiate global websocket object.
 * @todo: Add user cookie for authentication.
 */
var host = location.origin.replace(/^http/, 'ws')
var ws = new WebSocket(host +"/socket/" + location.pathname.replace('/room/', '').replace('/', ''));


/**
 * Helper function to get the value of a cookie.
 */
function cookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    // Bind the submit event of the form input to postMessage().
    $("#chat-input").submit(function() {
        postMessage($(this));
        return false;
    });
    $("#message-input").focus();
    //$('html, body').animate({scrollTop: $(document).height()}, 800);
    //$( "div.message" ).scrollTop( 1000 );
    var dimension = $('#daymessages').height()
    $('#daymessages').find(".message:last").slideDown("fast", function(){
    $('html, body, div').animate({scrollTop: dimension})//, 400);
    });
    // Connection state should be reflacted in submit button.
    var disabled = $("form#chat-input").find("textaera");
    disabled.attr("disabled", "disabled");

    // Websocket callbacks:
    ws.onopen = function() {
        console.log("Connected...");
        //disabled.removeAttr("disabled");
        $( "#messageArea" ).attr( "disabled", false );
        //$( "div.message" ).scrollTop( 1000 );
        //$( "div.content-container" ).scrollTop( 1000 );
        var dimension = $('#daymessages').height()
        $('#daymessages').find(".message:last").slideDown("fast", function(){
        $('html, body, div').animate({scrollTop: dimension})//, 400);
    });
    };
    ws.onmessage = function(event) {
        data = JSON.parse(event.data);
        if(data.textStatus && data.textStatus == "unauthorized") {
            alert("unauthorized");
            $( "#messageArea" ).attr( "disabled", true );
        }
        else if(data.error && data.textStatus) {
            alert(data.textStatus);
        }
        console.log("New Message", data);
        if (data.messages) {
            newMessages(data);

        }
    };
    ws.onclose = function() {
        // @todo: Implement reconnect.
        console.log("Closed!");
        $( "#messageArea" ).attr( "disabled", true );
    };
});


/**
 * Function to create a new message.
 */
function postMessage(form) {
    console.log('je suis deja dans postmessage')
    //var value = form.find("textaera[type=textaera]").val();
    var value = jQuery("textarea#messageArea").val();
    var message = {body: value};
    message.date = {date: value};
    message._xsrf = cookie("_xsrf");
    message.user = cookie("user");
    var disabled = form.find("input");
    //disabled.attr("disabled", "disabled");
    $( "#messageArea" ).prop( "disabled" );
    // Send message using websocket.
    ws.send(JSON.stringify(message));
    console.log(message)
    // @todo: A response if successful would be nice. 
    console.log("Created message (successfuly)");
    $("#messageArea").val("").select();
    //disabled.removeAttr("disabled");
    $( "#messageArea" ).prop( "disabled", false );
}


/**
 * Callback when receiving new messages.
 */
updater = {}
newMessages = function (data) {
    var messages = data.messages;
    if(messages.length == 0) return;
    updater.cursor = messages[messages.length - 1]._id;
    console.log(messages.length + "new messages, cursor: " + updater.cursor);
    for (var i = 0; i < messages.length; i++) {
        showMessage(messages[i]);
    }
};


/**
 * Function to add a bunch of (new) messages to the inbox.
 */
showMessage = function(message) {
    console.log("Show Message");
    var existing = $("#m" + message._id);
    if (existing.length > 0) console.log("probleme");//return;
    $("#daymessages").append('<div id = "9876543210" class="message-container"> \
    <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
    <div class="message"> \
    <div class="info"><a href="#" class="user-name">' + message.from + '</a><span class="info">' + message.date + '</span></div> \
    <div id="mymessage">' + message.body + '</div> \
    </div> \
    <a href="#" class="menu-btn"></a> \
    </div>');
    //$("#daymessages").append('<div id="9876543210" class="message-container" id="' + message._id + '"><b>' + message.from + ': </b>' + message.body + '</div>');
    //$.find(".message:last").slideDown("fast", function(){$('html, body').animate({scrollTop: $(document).height()}, 400)});
    //});
    //$("html, body").animate({$( "div.message:last" ).scrollTop( 1000 )};
    //var d = $('#message');
    //console.log(d)
    //d.scrollTop(d.prop("scrollHeight"));
    var dimension = $('#daymessages').height()
    $('#daymessages').find(".message:last").slideDown("fast", function(){
    $('html, body, div').animate({scrollTop: dimension})//, 4000);
    });

};
