/**
 * Initiate global websocket object.
 * @todo: Add user cookie for authentication.
 */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('_xsrf'));
            }
        }
    }
});
function cookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
//var bidule = 'chouette'
//var host = location.origin.replace(/^http/, 'ws')

/**
 * Helper function to get the value of a cookie.
 */

//var ws = new WebSocket(response);

//console.log('machin2' + machin.responseText)
// console.log('machin is' + machin);
// alert(machin.toSource)
//


//truc
//ws.onopen()
// function cookie(name) {
//     var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
//     return r ? r[1] : undefined;
// }

$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function () {
    };

    $.post("/room/testroom", function (data) {
        truc = JSON.parse(data); // John
        //console.log('test url is' + data[0]);
        // var ws = data
        // console.log(ws)
        ws = new WebSocket(truc.url);
        //console.log( data.time ); // 2pm
        // Websocket callbacks:
        ws.onopen = function () {
            console.log("Connected...");
            //disabled.removeAttr("disabled");
            $(".emojionearea-editor").attr("disabled", false);
            //$( "div.message" ).scrollTop( 1000 );
            //$( "div.content-container" ).scrollTop( 1000 );
            // var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
            // $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension.toFixed(0) + 'px; left: 0px;'}); // Can't handle Internet explorer like that because style output ins not the same order
            var dimension = $('.day-messages').height();
            $('html,body, div').animate({ scrollTop: dimension }, 1);
            // console.log("j'ai bidouillé mon div")
            // console.log($('#daymessages').height())
            console.log('dimension is' + dimension)
            //$('#daymessages').find(".message:last").slideDown("fast", function(){
            //$('html, body, div').animate({scrollTop: dimension})//, 400);
        };
        $("#chat-input").submit(function () {
            //e.default();
            postMessage($(this));
            console.log('chat-input');
            return false;
        });
        // $("#message-input").focus();
        var uploader = new ss.SimpleUpload({
            button: 'upload-btn', // HTML element used as upload button
            url: '/upload?' + window.location.pathname, // URL of server-side upload handler
            name: 'file1', // Parameter name of the uploaded file
            customHeaders: {'X-XSRFToken': cookie("_xsrf")}

        });
        console.log(cookie("_xsrf"))
        ws.onmessage = function (event) {
            data = JSON.parse(event.data);
            if (data.textStatus && data.textStatus == "unauthorized") {
                alert("unauthorized");
                $(".emojionearea-editor").attr("disabled", true);
            }
            else if (data.error && data.textStatus) {
                alert(data.textStatus);
            }
            console.log("New Message", data);
            if (data.messages) {
                newMessages(data);

            }
        };
        ws.onclose = function () {
            // @todo: Implement reconnect.
            console.log("Closed!");
            $(".emojionearea-editor").attr("disabled", true);
        };
//});


        /**
         * Function to create a new message.
         */
        function postMessage(form) {
            console.log('je suis deja dans postmessage')
            //var value = form.find("textaera[type=textaera]").val();
            var value = $(".emojionearea-editor").html();
            console.log(value);
            var message = {body: value};
            message.date = {date: value};
            message.type = {type: value};
            message._xsrf = cookie("_xsrf");
            message.user = cookie("user");
            var disabled = form.find("input");
            //disabled.attr("disabled", "disabled");
            $(".emojionearea-editor").prop("disabled");
            // Send message using websocket.
            ws.send(JSON.stringify(message));
            console.log(message)
            // @todo: A response if successful would be nice.
            console.log("Created message (successfuly)");
            //$("#messageArea").val("").select();
            $(".emojionearea-editor").html("")
            //disabled.removeAttr("disabled");
            $(".emojionearea-editor").prop("disabled", false);
            // var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
            // $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
            var dimension = $('.day-messages').height();
            $('html,body, div').animate({ scrollTop: dimension }, 1);
        }


        /**
         * Callback when receiving new messages.
         */
        updater = {}
        newMessages = function (data) {
            var messages = data.messages;
            console.log('je passe dans newMessages')
            if (messages.length == 0) return;
            updater.cursor = messages[messages.length - 1]._id;
            console.log(messages.length + "new messages, cursor: " + updater.cursor);
            for (var i = 0; i < messages.length; i++) {
                showMessage(messages[i]);
                console.log('message numero'[i]);
            }
        };


        /**
         * Function to add a bunch of (new) messages to the inbox.
         */
        showMessage = function (message) {
            console.log("Show Message");
            console.log('message type' + message.type);
            previoususer =  message.from
            var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
            stylecraft = 'position: relative; top: -' + dimension + 'px; left: 0px;'; // Todo: Do special handling for ie , who need rouding of values to 2 digits
            currentpos = $(mCSB_3_container).attr('style');
            console.log('currentpos is' + currentpos);
            console.log('stylecraft is' + stylecraft);
            var existing = $("#m" + message._id);
            console.log('existing' + existing);
            if (existing.length > 0) console.log("probleme");//return;
            if (message.type == 'file') {
                console.log('je suis un fichier')
                $(".messages_container").append('<div class="message-container"> \
                <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
                <div class="message"> \
                <div class="info"><a href="#" class="user-name">' + message.from + '</a><span class="info">' + message.date + '</span></div> \
                <div id="mymessage">' + message.body + '</div> \
                </div> \
                <a href="#" class="menu-btn"></a> \
                </div>');
                //currentpos = $(mCSB_3_container).attr('style');
                //console.log('currentpos is' + currentpos);
                //console.log('stylecraft is' + stylecraft);
                //if (currentpos !== stylecraft) return;
                //else {
                //    var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
                //    $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
                //}
                var dimension = $('.day-messages').height();
                $('html,body, div').animate({ scrollTop: dimension }, 1);
            }
            if (message.type == 'notification') {
                console.log("c'est une belle notif!");
                var notifcount = $('#notif-badge').text();
                console.log('notif count' + notifcount);
                $("#notification-widget").append('<p>' + message.body + '</p>');
                $("#notif-badge").text(notifcount = +notifcount + 1);
            }
            if (message.type == 'regular' && $('.message:last').find('#username:last').html() != message.from) {
                $(".day-messages").append('<div class="message-container"> \
                    <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
                    <div class="message"> \
                    <h6 id="username" hidden>{' + message.from + '</h6> \
                <div class="info"><a href="#" class="user-name">' + message.from + '</a><span class="info">' + message.date + '</span></div> \
                <div id="mymessage">' + message.body + '</div> \
                </div> \
                <div class="dropdown btn-group"> \
                <a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fa fa-ellipsis-h"></i></a> \
                <ul class="dropdown-menu users-checklist-dropdown dropdown-menu-right"> \
                    <li class="menu-visibility-option"><a href="#">Hide/Show #fileroom <i class="fa fa-eye" aria-hidden="true"></i><i class="fa fa-eye-slash" aria-hidden="true"></i></a></li> \
                    <li role="separator" class="divider"></li> \
                    <li><a href="#">Un-attache the file</a></li> \
                    <li><a href="#">Open a #fileroom</a></li> \
                    <li><a href="#">Download file</a></li> \
                    <li><a href="#">Add to filemanager</a></li> \
                        </ul> \
                    </div> \
                </div>');
                currentpos = $(mCSB_3_container).attr('style');
                console.log('currentpos is' + currentpos);
                console.log('stylecraft is' + stylecraft);
                // if (currentpos !== stylecraft) return;
                // else {
                //     var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
                //     $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
                // }
                var dimension = $('.day-messages').height();
                $('html,body, div').animate({ scrollTop: dimension }, 1);
                return
            }
            if (message.type == 'regular' && $('.message:last').find('#username:last').html() == message.from) {
                $(".day-messages").find('.messagefollow:last').append(message.body + '<br>');
                currentpos = $(mCSB_3_container).attr('style');
                console.log('currentpos is' + currentpos);
                console.log('stylecraft is' + stylecraft);
                // if (currentpos !== stylecraft) return;
                // else {
                //     var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
                //     $('#mCSB_3_container').attr({style: 'position: relative; top: -' + dimension + 'px; left: 0px;'});
                // }
                var dimension = $('.day-messages').height();
                $('html,body, div').animate({ scrollTop: dimension }, 1);
            }

        };
    });
});

//     //console.log('machin truc' + url);
//     // Bind the submit event of the form input to postMessage().
//     $("#chat-input").submit(function () {
//         postMessage($(this));
//         return false;
//     });
//
//     //$('html, body').animate({scrollTop: $(document).height()}, 800);
//     //$( "div.message" ).scrollTop( 1000 );
//     //var dimension = $('#daymessages').height()
//     //$('#daymessages').find(".message:last").slideDown("fast", function(){
//     //$('html, body, div').animate({scrollTop: dimension})//, 400);
//
//     // Connection state should be reflacted in submit button.
//     var disabled = $("form#chat-input").find("textaera");
//     disabled.attr("disabled", "disabled");
//

