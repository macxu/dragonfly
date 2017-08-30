
var app = angular.module("dragonflyJenkinsApp", []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);