$(function(){
    $(".scrollbar-section").mCustomScrollbar({
        alwaysShowScrollbar: 1
    });

    $('.right-sidebar-show-btn').on('click', rightSidebarOpenToggle);
    $('.notification-sidebar-show-btn').on('click', notificationSidebarOpenToggle);
    $('.close-panel-button').on('click', rightSidebarOpenToggle);
    $('.app-menu-show-btn').on('click', leftSidebarShowToggle);

    bodyResize();

    $(window).on('resize', bodyResize);

    // Drag and drop
    var panelList = $('#dragableList');
    panelList.sortable({
        handle: '.widget-header',
        update: function() {
            $('.widget', panelList).each(function(index, elem) {
                var $listItem = $(elem),
                    newIndex = $listItem.index();
            });
        }
    });

    // Input message
    var countVisibleRows = 4;
    var shiftKeyEvent = false;
    var inputMessage = $('#messageArea');
    inputMessage.val('');
    inputMessage.keydown(function(event){
        var footerHeight = $('.messages_footer').height();
        var rowCount = getRowsCount(inputMessage);

        if(event.shiftKey) shiftKeyEvent = true;

        if (event.keyCode == 13 && shiftKeyEvent){
            if(rowCount <= countVisibleRows){
                console.log(rowCount);
                inputMessage.prop('rows', rowCount + 1).css({'overflow-y': 'hidden'});
                $('#messages_container').css({'padding-bottom': (footerHeight + 20) + 'px' });
            }else {
                inputMessage.css({ 'overflow-y': 'scroll' });
            }

            var content = this.value;
            var caret = getCaret(this);
            event.stopPropagation();
        } else if(event.keyCode == 13) {
            event.preventDefault();
            $('form').submit();
        }
    });
    inputMessage.keyup(function(event){
        var rowCount = getRowsCount(inputMessage);
        var footerHeight = $('.messages_footer').height();
        if(event.shiftKey) shiftKeyEvent = false;

        if(rowCount <= countVisibleRows && event.keyCode != 13){
            inputMessage.prop('rows', rowCount).css({ 'overflow-y': 'hidden' });
            $('#messages_container').css({'padding-bottom': (footerHeight + 20) + 'px'});
        }else if (rowCount > countVisibleRows){
            inputMessage.css({ 'overflow-y': 'scroll' });
        }
    });
});

function leftSidebarShowToggle(){
    $('.left-sidebar').toggleClass('min');
}

function rightSidebarOpenToggle(){
    $('#notification_sidebar').attr({class: 'sidebar notification-sidebar hidden'})
    $('#right_sidebar').toggleClass('hidden');
}
function notificationSidebarOpenToggle(){
    // $('#right_sidebar').toggleClass('hidden');
    $('#right_sidebar').attr({class: 'sidebar right-sidebar hidden'})
    $('#notification_sidebar').toggleClass('hidden');
}

function bodyResize(){
    var headerHeight = $('.top-bar').height();
    var windowHeight = $(window).height();
    var resultHeight = windowHeight - headerHeight - 20;

    $('#left_sidebar').css({'height': resultHeight + 'px'});
    $('.content_container').css({'height': resultHeight + 'px'});
    $('#right_sidebar').css({'height': resultHeight + 'px'});
}

function getCaret(el) {
    if (el.selectionStart) {
        return el.selectionStart;
    } else if (document.selection) {
        el.focus();

        var r = document.selection.createRange();
        if (r == null) {
            return 0;
        }

        var re = el.createTextRange(),
            rc = re.duplicate();
        re.moveToBookmark(r.getBookmark());
        rc.setEndPoint('EndToStart', re);

        return rc.text.length;
    }
    return 0;
}

function getRowsCount(elem){
    var text = elem.val();
    var lines = text.split(/\r|\r\n|\n/);

    return lines.length;
}