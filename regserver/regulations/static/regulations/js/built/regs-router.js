define("regs-router",["underscore","backbone","dispatch","queryparams"],function(e,t,n){var r=t.Router.extend({routes:{"regulation/:section/:version":"backToSection","search/:reg":"backToSearchResults"},backToSection:function(e){n.trigger("openSection:set",e),n.trigger("sxs:close")},backToSearchResults:function(e,t){var r={query:t.q,version:t.version};typeof t.page!="undefined"&&(r.page=t.page),n.trigger("searchResults:back",r)},start:function(){var e=n.getURLPrefix()||"/";t.history.start({pushState:"pushState"in window.history,silent:!0,root:e})}}),i=new r;return i});