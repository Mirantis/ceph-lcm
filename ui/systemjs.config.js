(function(global) {

  var paths = {
    'npm:': 'node_modules/'
  };

  var map = {
    'app': 'app',

    '@angular/core': 'npm:@angular/core/bundles/core.umd.js',
    '@angular/common': 'npm:@angular/common/bundles/common.umd.js',
    '@angular/compiler': 'npm:@angular/compiler/bundles/compiler.umd.js',
    '@angular/platform-browser': 'npm:@angular/platform-browser/bundles/platform-browser.umd.js',
    '@angular/platform-browser-dynamic': 'npm:@angular/platform-browser-dynamic/bundles/platform-browser-dynamic.umd.js',
    '@angular/http': 'npm:@angular/http/bundles/http.umd.js',
    '@angular/router': 'npm:@angular/router/bundles/router.umd.js',
    '@angular/forms': 'npm:@angular/forms/bundles/forms.umd.js',
    'rxjs': 'npm:rxjs',
    'angular2-in-memory-web-api': 'npm:angular2-in-memory-web-api',

    'lodash': 'npm:lodash/lodash.js',
    'js-data': 'npm:js-data',
    'js-data-http': 'npm:js-data-http',
    'angular2-cookie': 'npm:angular2-cookie',

    'jquery': 'npm:jquery',
    'bootstrap': 'npm:bootstrap',
    'format-json': 'npm:format-json',
    'file-saver': 'npm:file-saver'
  };

  var packages = {
    'app': {
      main: 'main.js',
      defaultExtension: 'js'
    },
    'rxjs': {
      defaultExtension: 'js'
    },
    'angular2-in-memory-web-api': {
      main: 'index.js',
      defaultExtension: 'js'
    },
    'js-data': {
      main: 'dist/js-data.js'
    },
    'js-data-http': {
      main: 'dist/js-data-http.js'
    },
    'angular2-cookie': {
      main: 'core.js'
    },
    'jquery': {
      main: 'dist/jquery.min.js'
    },
    'bootstrap': {
      main: 'dist/js/bootstrap.min.js'
    },
    'format-json': {
      main: 'index.js'
    },
    'file-saver': {
      main: 'FileSaver.js'
    }
  };

  System.config({
    paths: paths,
    map: map,
    packages: packages
  });

})(this);
