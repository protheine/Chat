$.fn.pageMe = function ( opts ) {
    var $this    = this,
        defaults = {
            perPage        : 7,
            showPrevNext   : false,
            hidePageNumbers: false
        },
        settings = $.extend( defaults, opts );

    var listElement = $this;
    var perPage     = settings.perPage;
    var children    = listElement.children();
    var pager       = $( '.pager' );

    if ( typeof settings.childSelector != "undefined" ) {
        children = listElement.find( settings.childSelector );
    }

    if ( typeof settings.pagerSelector != "undefined" ) {
        pager = $( settings.pagerSelector );
    }

    var numItems = children.size();
    var numPages = Math.ceil( numItems / perPage );

    pager.data( "curr", 0 );

    if ( settings.showPrevNext ) {
        $( '<li><a href="#" class="prev_link">«</a></li>' ).appendTo( pager );
    }

    var curr = 0;
    while ( numPages > curr && (settings.hidePageNumbers == false) ) {
        $( '<li><a href="#" class="page_link">' + (curr + 1) + '</a></li>' ).appendTo( pager );
        curr++;
    }

    if ( settings.showPrevNext ) {
        $( '<li><a href="#" class="next_link">»</a></li>' ).appendTo( pager );
    }

    pager.find( '.page_link:first' ).addClass( 'active' );
    pager.find( '.prev_link' ).hide();
    if ( numPages <= 1 ) {
        pager.find( '.next_link' ).hide();
    }
    pager.children().eq( 1 ).addClass( "active" );

    children.hide();
    children.slice( 0, perPage ).show();

    pager.find( 'li .page_link' ).click(
        function () {
            var clickedPage = $( this ).html().valueOf() - 1;
            goTo( clickedPage, perPage );
            return false;
        }
    );
    pager.find( 'li .prev_link' ).click(
        function () {
            previous();
            return false;
        }
    );
    pager.find( 'li .next_link' ).click(
        function () {
            next();
            return false;
        }
    );

    function previous() {
        var goToPage = parseInt( pager.data( "curr" ) ) - 1;
        goTo( goToPage );
    }

    function next() {
        goToPage = parseInt( pager.data( "curr" ) ) + 1;
        goTo( goToPage );
    }

    function goTo( page ) {
        var startAt = page * perPage,
            endOn   = startAt + perPage;

        children.css( 'display', 'none' ).slice( startAt, endOn ).show();

        if ( page >= 1 ) {
            pager.find( '.prev_link' ).show();
        }
        else {
            pager.find( '.prev_link' ).hide();
        }

        if ( page < (numPages - 1) ) {
            pager.find( '.next_link' ).show();
        }
        else {
            pager.find( '.next_link' ).hide();
        }

        pager.data( "curr", page );
        pager.children().removeClass( "active" );
        pager.children().eq( page + 1 ).addClass( "active" );

    }
};
$(
    function () {

        $('#chat-input').on('keydown', '.emojionearea-editor', function (e) {
            var height = $('.messages_footer').height() + 9;
            $('#messages_container .scrollbar-section').css('height', 'calc(100% - '+ height +'px)');
        });

        var inputMessage = $( '#messageArea' );

        // Smiles init
        var smiles = inputMessage.emojioneArea(
            {
                pickerPosition  : "top",
                filtersPosition : "top",
                autocomplete    : false,
                hidePickerOnBlur: false,
                buttonLabel     : 'Add Emoji',
                buttonPosition  : 'left'
            }
        );

        $(document).click(function(event) {
            if($(event.target).closest('.emojionearea-wrapper').length <= 0) {
                if($('.emojionearea-button').hasClass('active')) {
                    $('.emojionearea-button').toggleClass('active');
                }
            }
        });


        $( ".scrollbar-section" ).mCustomScrollbar(
            {
                alwaysShowScrollbar: 0,
                //scrollInertia: 100
            }
        );

        $( '.menu-visibility-option' ).on(
            'click', function () {
                $( this ).toggleClass( 'not-visible' );
            }
        );

        $( '.right-sidebar-show-btn' ).on( 'click', rightSidebarOpenToggle );
        $( '.close-panel-button' ).on( 'click', rightSidebarOpenToggle );
        $( '.app-menu-show-btn' ).on( 'click', leftSidebarShowToggle );

        //contentWidth( '.content_container, #messages_container', '#left_sidebar', '#right_sidebar' );

        //bodyResize();

        //$( window ).on( 'resize', bodyResize );

        // Drag and drop
        var panelList = $( '#dragableList' );
        panelList.sortable(
            {
                handle: '.widget-header',
                update: function () {
                    $( '.widget', panelList ).each(
                        function ( index, elem ) {
                            var $listItem = $( elem ),
                                newIndex  = $listItem.index();
                        }
                    );
                }
            }
        );

        // Dropdown scripts
        $( '.dropdown-menu' ).on(
            'click', function ( e ) {
                e.stopPropagation();
            }
        );
        $( '.dropdown-close-btn' ).on(
            'click', function ( e ) {
                $( '.dropdown.open .dropdown-toggle' ).dropdown( 'toggle' );
            }
        );

        $( '.colorpicker-component' ).colorpicker();

        // Input message
        var countVisibleRows = 4;
        var shiftKeyEvent    = false;

        /*$( ".dropdown-toggle" ).click(
            function () {
                var widget   = $( this ).closest( '.widget-content' ),
                    dropdown = $( this ).next();
                //dropdown.outerHeight()
                widget.css( 'height', "auto" )
                widget.css( 'height', !dropdown.is( ":visible" ) ? widget.outerHeight() + dropdown.outerHeight() : "auto" )


            }
        );*/
        $( '.widget-content' ).click(
            function ( e ) {
                var dropdown = $( this ).find( 'ul' );
                if ( e.target.tagName != "I" ) {
                    $( this ).css( 'height', "auto" )
                }
            }
        )

        // own code
        $('#sidebar-user-search').on('input', function() {
            var search = $(this).val().toLowerCase().trim(),
                users = $(this).closest('.dropdown-menu').find('li .user-name');
            users.closest('li').hide();
            users.each(function () {
                if($(this).text().toLowerCase().indexOf(search) == 0) {
                    $(this).closest('li').show();
                }
            })
        });

        // this needed because emojionearea plugin loading after page loaded with delay 0.5 s
        setTimeout(
            function () {
                var emojiareaField = $( 'body' ).find( '.emojionearea-editor' );
                var footerHeight;
                emojiareaField.keydown(
                    function ( event ) {
                        if ( event.keyCode == 13 ) {
                            if ( !event.shiftKey ) {
                                event.stopPropagation();
                                event.preventDefault();
                                console.log('enter pressed');
                                $('#chat-input').submit()
                            }
                        }
                        footerHeight = $( '.messages_footer' ).outerHeight();
                        //$( "#messages_container" ).css( 'padding-bottom', footerHeight )
                    }
                );
            }, 1000
        );


        $( '.data-table' ).DataTable(
            {
                "bFilter"  : false,
                "bPaginate": false,
                "info"     : false
            }
        );

        $( '.data-table-search' ).DataTable(
            {
                "bFilter"  : true,
                "bPaginate": false,
                "info"     : false
            }
        );

        //$('#userTable').pageMe({pagerSelector:'#myPager',showPrevNext:true,hidePageNumbers:false,perPage:4});

    }
);

function contentWidth( contentWrapper, leftSidebar, rightSidebar ) {
    var window_width   = $( window ).width(),
        left_sb_width  = $( leftSidebar ).width(),
        right_sb_width = $( rightSidebar ).is( ":visible" ) ? $( rightSidebar ).width() : 0,
        content_width  = window_width - (left_sb_width + right_sb_width);

    $( contentWrapper ).width( content_width );
}

function leftSidebarShowToggle() {
    $('.left-sidebar').toggleClass('min');
    $('.content_container').toggleClass('app-menu-hidden');
    //contentWidth( '.content_container, #messages_container', '#left_sidebar', '#right_sidebar' );
}

function rightSidebarOpenToggle() {
    $( '#right_sidebar' ).toggleClass('hidden');
    $( '.content_container' ).toggleClass('rightbar-hidden');
    //contentWidth( '.content_container, #messages_container', '#left_sidebar', '#right_sidebar' );
}

function bodyResize() {

}

function getCaret( el ) {
    if ( el.selectionStart ) {
        return el.selectionStart;
    } else if ( document.selection ) {
        el.focus();

        var r = document.selection.createRange();
        if ( r == null ) {
            return 0;
        }

        var re = el.createTextRange(),
            rc = re.duplicate();
        re.moveToBookmark( r.getBookmark() );
        rc.setEndPoint( 'EndToStart', re );

        return rc.text.length;
    }
    return 0;
}

function getRowsCount( elem ) {
    var text  = elem.val();
    var lines = text.split( /\r|\r\n|\n/ );

    return lines.length;
}

function checkForChanges() {
    if ( $element.css( 'height' ) != lastHeight ) {
        alert( 'xxx' );
        lastHeight = $element.css( 'height' );
    }

    setTimeout( checkForChanges, 500 );
}

