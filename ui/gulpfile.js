/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

var gulp = require('gulp');
var concat = require('gulp-concat');
var tsc = require('gulp-typescript');
var tsProject = tsc.createProject('tsconfig.json');
var sourcemaps = require('gulp-sourcemaps');
var minify = require('gulp-minify');
var sysBuilder = require('systemjs-builder');
var runSequence = require('run-sequence');
var less = require('gulp-less');
var autoprefixer = require('autoprefixer');
var cssnano = require('cssnano');
var postcss = require('gulp-postcss')
var googleWebFonts = require('gulp-google-webfonts');
var replace = require('gulp-replace');
var rimraf = require('rimraf');

// Bundle dependencies into vendors file
gulp.task('bundle:libs', function () {
  return gulp.src([
    'node_modules/core-js/client/shim.min.js',
    'node_modules/zone.js/dist/zone.js',
    'node_modules/reflect-metadata/Reflect.js',
    'node_modules/systemjs/dist/system.src.js',
    'systemjs.config.js'
  ])
    .pipe(concat('vendors.js'))
    .pipe(minify({
      ext: {
        min: '.min.js'
      },
      noSource: true
    }))
    .pipe(gulp.dest('build/tmp/js'));
});

// Compile TypeScript into javascript
gulp.task('compile:ts', function () {
  return tsProject.src()
  .pipe(tsProject())
  .js.pipe(gulp.dest('./'));
});

// Enables production mode in bundle
gulp.task('modify:prod-mode', function () {
  return gulp.src('app/main.js')
  .pipe(replace('(!!0)', '(!0)'))
  .pipe(gulp.dest('app'));
});

// Generate systemjs-based build
gulp.task('bundle:js', ['modify:prod-mode'], function () {
  var builder = new sysBuilder('./', 'systemjs.config.js');
  return builder.buildStatic('app', 'build/tmp/js/app.min.js', {
    minify: true,
    mangle: true
  });
});

// Merges all scripts into one file
gulp.task('concat:js', function () {
  // Order should be preserved
  return gulp.src([
    'build/tmp/js/vendors.min.js',
    'build/tmp/js/app.min.js'
  ])
  .pipe(concat('decapod.min.js'))
  .pipe(gulp.dest('build/js'))
});

// Bundle app scripts and external libs
gulp.task('build:js', function (callback) {
  runSequence('compile:ts', 'bundle:js', 'bundle:libs', 'concat:js', callback);
});

// Download google fonts locally and create
// reference css for inclusion
gulp.task('fonts:css', function () {
  return gulp.src('google_fonts.list')
  .pipe(googleWebFonts({
    fontsDir: '',
    cssDir: '',
    cssFilename: 'fonts.css'
  }))
  .pipe(gulp.dest('build/fonts'));
});

// Builds styles
gulp.task('build:styles', ['fonts:css'], function () {
  return gulp.src('app/styles/styles.less')
  .pipe(less())
  .pipe(postcss([
    autoprefixer(),
    cssnano()
  ]))
  .pipe(gulp.dest('build/styles/'));
});

// Copies images into build directory
gulp.task('copy:images', function () {
  return gulp.src('app/images/*.*')
  .pipe(gulp.dest('build/images'));
});

// Copy templates
gulp.task('copy:templates', function () {
  return gulp.src('app/templates/**/*.html')
  .pipe(gulp.dest('build/app/templates'));
});

// Copy glyphicon fonts from bootstrap
gulp.task('fonts:bootstrap', function () {
  return gulp.src('node_modules/bootstrap/fonts/*.*')
  .pipe(gulp.dest('build/fonts/'));
});

// Copy static resources
gulp.task('copy:statics', ['copy:images', 'copy:templates', 'fonts:bootstrap']);

// Cleanup building artifacts
gulp.task('cleanup', function (callback) {
  return rimraf('build/tmp', callback);
});

// Modifies index.html with the proper references
gulp.task('modify:index', function () {
  return gulp.src('index.html')
  .pipe(replace('href="app/', 'href="'))
  .pipe(replace(/<\!---->[\s\S]+-->/m, '    <script src="js/decapod.min.js"></script>'))
  .pipe(replace(/\s*<script>[\s\S]+<\/script>/m, ''))
  .pipe(gulp.dest('build'));
});

// Modifies endpoint to be host-independent
gulp.task('modify:endpoint', function () {
  return gulp.src('build/js/**/*.js')
  .pipe(replace('http://localhost:9999/v', '/v'))
  .pipe(gulp.dest('build/js'));
});

// Production modifications
gulp.task('modifications', ['modify:index', 'modify:endpoint']);

// Builds the whole project and updates references
gulp.task('default', function (callback) {
  runSequence(
    ['build:js', 'build:styles', 'copy:statics'],
    ['modifications', 'cleanup'],
    callback
  );
});
