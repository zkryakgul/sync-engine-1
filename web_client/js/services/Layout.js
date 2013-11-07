'use strict';

// fucking linter
var angular = angular,
    $ = $,
    console = console;


angular.module('InboxApp.services')
.factory('Layout', function() {

    // This should all be done on doc load
    var windowSize = {
        height: 0,
        width: 0,
        headersHeight: 0,
        mainHeight: 0,
        contentBodyHeight: 0,
        contentBodyWidth: 0,
        leftNavHeight: 0,
        contentDetailsWidth: 0,
        setDimensions: function() {
            windowSize.height = $('body').height();
            windowSize.width = $('body').width();

            windowSize.headerHeight = $('.header').outerHeight(true);
            windowSize.mainHeight = windowSize.height - windowSize.headerHeight;

            windowSize.rightContentWidth = windowSize.width - $('.sidebar').outerWidth(true);

            windowSize.contentBodyHeight = windowSize.mainHeight  - $('.action_bar_top').outerHeight(true);

            windowSize.contentBodyWidth = $('.right_panel_container').width();


            windowSize.sidebarWidth = $('.sidebar').outerWidth(true);
            windowSize.masterPaneWidth = $('.master_pane').outerWidth(true);
            windowSize.detailPaneWidth = windowSize.width - windowSize.sidebarWidth - windowSize.masterPaneWidth;


            windowSize.updateSizes();
        },
        updateSizes: function() {
            $('#main').css('height', windowSize.height + 'px');

            $('.header').css('width', windowSize.width + 'px');

            $('.height_main').css('height', windowSize.mainHeight + 'px');

            var messagelist_height = windowSize.mainHeight - $('.category_bar').outerHeight(true);
            $('.messagelist').css('height', messagelist_height + 'px');

            var container_scrollable_height = windowSize.mainHeight - parseInt($('.master_pane').css('margin-top'));
            $('.container_scrollable').css('height', container_scrollable_height + 'px');

            var full_composer_container_height = windowSize.mainHeight - parseInt($('.full_composer_container').css('margin-top'));
            $('.full_composer_container').css('height', full_composer_container_height + 'px');
            var fullcomposeview_body_height = full_composer_container_height - 155;
            $('.fullcomposeview_body').css('height', fullcomposeview_body_height + 'px');


            $('.detail_pane').css('width', windowSize.detailPaneWidth + 'px');

            // $('.panel_right_content').css('width', windowSize.rightContentWidth + 'px');

            $('.right_panel_container').css('width', windowSize.rightContentWidth + 'px');
            $('.right_panel_container').css('height', (windowSize.contentBodyHeight) + 'px');

        },
        init: function() {
            if ($('#main').length) {
                windowSize.setDimensions();
                $(window).resize(function() {
                    windowSize.setDimensions();
                });
            }
        }
    };
    $(document).ready(function() {
        windowSize.init();
    });


    return {
        reflow: function() {
            windowSize.setDimensions();
        },

    }
});
