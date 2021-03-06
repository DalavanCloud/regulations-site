if (typeof process === 'object') {
  // Initialize node environment
  global.chai = require('chai');
  global.expect = require('chai').expect;
  var plugin  = require("chai-jq");
  global.chai.use(plugin);

  require('jsdom-global')();
} else {
  window.expect = window.chai.expect;
  window.require = function() { /* noop */ };
}
