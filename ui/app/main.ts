import {bootstrap}    from '@angular/platform-browser-dynamic';
import {AppComponent} from './components/app';
import {APP_ROUTES_PROVIDER} from './app.routes';
import {CookieService} from 'angular2-cookie/core';
import {SessionService, LoggedIn} from './services/session'
import {AuthService} from './services/auth'
import {HTTP_PROVIDERS} from '@angular/http';
import {BaseApiService} from './services/base';

bootstrap(AppComponent, [
  APP_ROUTES_PROVIDER,
  HTTP_PROVIDERS,
  CookieService,
  AuthService,
  SessionService,
  LoggedIn,
  BaseApiService
]);
