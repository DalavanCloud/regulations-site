// **Extends** Backbone.View
//
// **Usage** ```require(['drawer-view'], function(DrawerView) {})```
//
// **Jurisdiction** Left panel drawer container
define('drawer-view', ['jquery', 'underscore', 'backbone', 'toc-view', 'history-view', 'search-view'], function($, _, Backbone, TOCView, HistoryView, SearchView) {
    'use strict';

    var DrawerView = Backbone.View.extend({
        el: '#menu',

        initialize: function() {
            var openTab,
                k,
                path = Dispatch.getDrawerState();

            Dispatch.on('drawer:stateChange', this.changeContents, this);

            this.$label = $('.toc-type');
            this.$children = $('.toc-container');
            this.childViews = {
                'table-of-contents': {
                    'selector': $('#table-of-contents'),
                    'constructor': TOCView
                },
                'timeline': {
                    'selector': $('#timeline'),
                    'constructor': HistoryView
                },
                'search': {
                    'selector': $('#search'),
                    'constructor': SearchView
                }
            };

            // sets default tab for search
            if (path) {
                for (k in this.childViews) {
                    if (this.childViews.hasOwnProperty(path)) {
                        openTab = path;
                    }
                }
            }

            openTab = openTab || 'table-of-contents';

            // initialize child view to populate drawer
            this.changeContents(openTab); 
        },

        changeContents: function(activeId) {
            // hide the content of all drawer sections
            this.$children.addClass('hidden');

            // remove the 'hidden' class from the active drawer section
            this.childViews[activeId]['selector'].removeClass('hidden');

            // create a new childView if a view doesn't already exist
            this.childViews[activeId].view = this.childViews[activeId].view || new this.childViews[activeId].constructor();
            Dispatch.set('drawerState', activeId);
        }

    });

    return DrawerView;
});
