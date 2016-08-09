import {APP_ROUTES_PROVIDER} from './app.routes';
import {HTTP_PROVIDERS} from '@angular/http';
import {bootstrap}    from '@angular/platform-browser-dynamic';
import {AppComponent} from './components/app';
import {CookieService} from 'angular2-cookie/core';
import {SessionService, LoggedIn} from './services/session'
import {AuthService} from './services/auth'
import {DataService} from './services/data';

bootstrap(AppComponent, [
  APP_ROUTES_PROVIDER,
  HTTP_PROVIDERS,
  CookieService,
  AuthService,
  SessionService,
  LoggedIn,
  DataService
]);
