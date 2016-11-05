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
    //var dimension = $('#daymessages').height()
    //$('#daymessages').find(".message:last").slideDown("fast", function(){
    //$('html, body, div').animate({scrollTop: dimension})//, 400);

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
        var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
        $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
        // console.log("j'ai bidouillé mon div")
        // console.log($('#daymessages').height())
        console.log('dimension is' + dimension)
        //$('#daymessages').find(".message:last").slideDown("fast", function(){
        //$('html, body, div').animate({scrollTop: dimension})//, 400);
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
    console.log('je passe dans newMessages')
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
    var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
        stylecraft = 'position: relative; top: -' + dimension +'px; left: 0px;';
    currentpos =  $(mCSB_3_container).attr('style');
    console.log('currentpos is' + currentpos);
    console.log('stylecraft is' + stylecraft);
    var existing = $("#m" + message._id);
    if (existing.length > 0) console.log("probleme");//return;
    $("#daymessages").append('<div class="message-container"> \
    <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
    <div class="message"> \
    <div class="info"><a href="#" class="user-name">' + message.from + '</a><span class="info">' + message.date + '</span></div> \
    <div id="mymessage">' + message.body + '</div> \
    </div> \
    <a href="#" class="menu-btn"></a> \
    </div>');
    currentpos =  $(mCSB_3_container).attr('style');
    console.log('currentpos is' + currentpos);
    console.log('stylecraft is' + stylecraft);
    if (currentpos !== stylecraft) return;
    else {
        var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
        $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
    }


};
