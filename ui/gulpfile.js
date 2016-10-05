var gulp = require('gulp');
var concat = require('gulp-concat');
var tsc = require('gulp-typescript');
var tsProject = tsc.createProject('tsconfig.json');
var sourcemaps = require('gulp-sourcemaps');
var minify = require('gulp-minify');
var sysBuilder = require('systemjs-builder');
var runSequence = require('run-sequence');
var less = require('gulp-less');
var cssmin = require('gulp-cssmin');
var googleWebFonts = require('gulp-google-webfonts');
var replace = require('gulp-replace');

// Bundle dependencies into vendors file
gulp.task('bundle:libs', function () {
  return gulp.src([
    'node_modules/core-js/client/shim.min.js',
    'node_modules/zone.js/dist/zone.js',
    'node_modules/reflect-metadata/Reflect.js',
    'node_modules/systemjs/dist/system.src.js',
    'systemjs.config.js',
    ])
    .pipe(concat('vendors.min.js'))
    .pipe(gulp.dest('build/js'));
});

// Fix typings for jquery
gulp.task('fix-typings', function () {
  return gulp.src('typings/globals/jquery/index.d.ts')
  .pipe(replace('export = $;', 'export = jQuery;'))
  .pipe(replace('declare var $: JQueryStatic;', ''))
  .pipe(gulp.dest('typings/globals/jquery'));
});

// Compile TypeScript into javascript
gulp.task('compile:ts', ['fix-typings'], function () {
  return tsProject.src()
  .pipe(tsProject())
  .js.pipe(gulp.dest('build/tmp'));
});

// Generate systemjs-based build
gulp.task('bundle:js', function () {
  var builder = new sysBuilder('./', './systemjs.config.js');
  return builder.buildStatic('app', 'build/tmp/app.js');
});

// Minify javascript bundle
gulp.task('minify:js', function () {
  return gulp.src('build/tmp/*.js')
  .pipe(minify({
    ext: {
      min: '.min.js'
    },
    noSource: true
  }))
  .pipe(gulp.dest('build/js/'));
});

// Compile less styles into css
gulp.task('styles:less', function () {
  return gulp.src('app/styles/styles.less')
  .pipe(less())
  .pipe(cssmin({
    processImport: true,
    keepBreaks: true
  }))
  .pipe(gulp.dest('build/styles/'));
});

// Download google fonts locally and create
// reference css for inclusion
gulp.task('fonts:css', function () {
  return gulp.src('google_fonts.list')
  .pipe(googleWebFonts({
    fontsDir: 'fonts',
    cssDir: 'styles',
    cssFilename: 'fonts.css'
  }))
  .pipe(gulp.dest('build'));
});

// Copy glyphicon fonts from bootstrap
gulp.task('fonts:bootstrap', function () {
  return gulp.src('node_modules/bootstrap/fonts/*.*')
  .pipe(gulp.dest('build/fonts/'));
});

// Bundle app scripts and external libs
gulp.task('build:js', function (callback) {
  runSequence('compile:ts', 'bundle:js', ['bundle:libs', 'minify:js'], callback);
});

// Builds styles
gulp.task('build:styles', function (callback) {
  return runSequence('fonts:css', ['styles:less', 'fonts:bootstrap'], callback);
});

// Copies images into build directory
gulp.task('images', function () {
  return gulp.src('app/images/*.*')
  .pipe(gulp.dest('build/images'));
});

// Builds the whole project and updates references
gulp.task('build', ['build:js', 'build:styles', 'images'], function () {
  return gulp.src('index.html')
  .pipe(replace('"app/styles', '"styles'))
  .pipe(replace(/<\!---->[\s\S]+-->/m, '    <script src="js/vendors.min.js"></script>\n    <script src="js/app.min.js"></script>'))
  .pipe(gulp.dest('build'));
});