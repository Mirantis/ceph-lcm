import {bootstrap}    from '@angular/platform-browser-dynamic';
import {AppComponent} from './components/app';
import {APP_ROUTES_PROVIDER} from './app.routes';
import {CookieService} from 'angular2-cookie/core';
import {AuthService, LoggedIn} from './services/auth'
import {HTTP_PROVIDERS} from '@angular/http';

bootstrap(AppComponent, [
  APP_ROUTES_PROVIDER,
  HTTP_PROVIDERS,
  CookieService,
  AuthService,
  LoggedIn
]);
