define("search-view",["jquery","underscore","backbone","dispatch","search-results-view"],function(e,t,n,r,i){var s=n.View.extend({el:"#search",events:{submit:"openSearchResults"},openSearchResults:function(t){t.preventDefault();var n=e(t.target);r.setContentView(new i({query:n.find("input[name=q]")[0].value,version:n.find("select[name=version]")[0].value})),r.set("contentClass","search-results")}});return s});