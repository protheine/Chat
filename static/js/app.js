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
/**
 * Helper function to get the value of a cookie.
 */

$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function () {
    };

    $.post("/room/testroom", function (data) {
        truc = JSON.parse(data);
        ws = new WebSocket(truc.url);
        // Websocket callbacks:
        ws.onopen = function () {
            console.log("Connected...");
            $(".emojionearea-editor").attr("disabled", false);
            var dimension = $('.day-messages').height();
            $('html,body, div').animate({ scrollTop: dimension }, 1);
            console.log('dimension is' + dimension)
        };
        $("#chat-input").submit(function () {
            //e.default();
            postMessage($(this));
            console.log('chat-input');
            return false;
        });
        console.log(cookie("_xsrf"))
        ws.onmessage = function (event) {
            data = JSON.parse(event.data);
            console.log('data is' + data)
            if (data.textStatus && data.textStatus == "unauthorized") {
                alert("unauthorized");
                $(".emojionearea-editor").attr("disabled", true);
            }
            else if (data.error && data.textStatus) {
                alert(data.textStatus);
            }
            console.log("New Message", data);
            if (data.messages) {
                console.log('ok');
                //console.log(data.messages);
                newMessages(data);

            }
        };
        ws.onclose = function () {
            // @todo: Implement reconnect.
            console.log("Closed!");
            $(".emojionearea-editor").attr("disabled", true);
        };

        /**
         * Function to create a new message.
         */
        function postMessage(form) {
            console.log('je suis deja dans postmessage')
            var value = $(".emojionearea-editor").html();
            console.log(value);
            var message = {body: value};
            message.date = {date: value};
            message.type = {type: value};
            message._xsrf = cookie("_xsrf");
            message.user = cookie("user");
            var disabled = form.find("input");
            $(".emojionearea-editor").prop("disabled");
            // Send message using websocket.
            ws.send(JSON.stringify(message));
            console.log(message)
            // @todo: A response if successful would be nice.
            console.log("Created message (successfuly)");
            $(".emojionearea-editor").html("")
            $(".emojionearea-editor").prop("disabled", false);
            scrollToBottom($('.messages_container .messages_wrapper'));
        }


        /**
         * Callback when receiving new messages.
         */
        updater = {}
        newMessages = function (data) {
            var messages = data.messages;
            console.log('je passe dans newMessages')
            if (messages.length == 0) console.log('length est 0');//return;
            updater.cursor = messages[messages.length - 1]._id;
            console.log(messages.length + "new messages, cursor: " + updater.cursor);
            for (var i = 0; i < messages.length; i++) {
            showMessage(messages[i]);
            }
        };


        /**
         * Function to add a bunch of (new) messages to the inbox.
         */
        showMessage = function (message) {
            console.log("Show MMMMMessage");
            console.log('mmmmmessage type ' + message.type);
            previoususer =  message.from
            //var dimension = $('#mCSB_3_container').height() - $('#mCSB_3_scrollbar_vertical').height();
            //stylecraft = 'position: relative; top: -' + dimension + 'px; left: 0px;'; // Todo: Do special handling for ie , who need rouding of values to 2 digits
            //currentpos = $(mCSB_3_container).attr('style');
            //console.log('currentpos is' + currentpos);
            //console.log('stylecraft is' + stylecraft);
            var existing = $("#m" + message._id);
            console.log('existing ' + existing);
            if (existing.length > 0) console.log("probleme");//return;
            if (message.type == 'file') {
                console.log('je suis un fichier')
                $(".messages_container").append('<div class="message-container"> \
                <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
                <div class="message"> \
                    <h6 id="username" hidden>' + message.from + '</a><span class="info">' + message.date + '</span></div> \
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
                //var dimension = $('.day-messages').height();
                //$('html,body, div').animate({ scrollTop: dimension }, 1);
                scrollToBottom($('.messages_container .messages_wrapper'));
            }
            console.log(message.type);
            if (message.type == 'notification') {
                console.log("c'est une belle notif!");
                var notifcount = $('#notif-badge').text();
                console.log('notif count' + notifcount);
                $("#notification-widget").append('<p>' + message.body + '</p>');
                $("#notif-badge").text(notifcount = +notifcount + 1);
            }
            if (message.type == 'regular' && $('.message:last').find('#username:last').html() != message.from) {
                console.log('regular');
                $(".day-messages").append('<div class="message-container"> \
                    <a href="#" class="thumbnail user-avatar"><img src="../static/images/user-avatar.png" alt=""></a> \
                    <div class="message"> \
                    <h6 id="username" hidden>{' + message.from + '</h6> \
                <div class="info"><a href="#" class="user-name">' + message.from + '</a><span class="info">' + message.date + '</span></div> \
                <div class="content-message">' + message.body + '</div> \
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
                //var dimension = $('.day-messages').height();
                //$('html,body, div').animate({ scrollTop: dimension }, 1);
                scrollToBottom($('.messages_container .messages_wrapper'));
                return
            }
            if (message.type == 'regular' && $('.message:last').find('#username:last').html() == message.from) {
                console.log('completement')
                $(".day-messages").find('.messagefollow:last').append(message.body + '<br>');

                scrollToBottom($('.messages_container .messages_wrapper'));
                //currentpos = $(mCSB_3_container).attr('style');
                //console.log('currentpos is' + currentpos);
                //console.log('stylecraft is' + stylecraft);
                //var dimension = $('.day-messages').height();
                //$('html,body, div').animate({ scrollTop: dimension }, 1);
            }
        };
    });
});
