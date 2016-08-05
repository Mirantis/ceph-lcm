import {Injectable} from '@angular/core';
import {Http, Headers} from '@angular/http';
import {CookieService} from 'angular2-cookie/core';
import {Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
import {Observable} from 'rxjs/Observable';
import {SessionService} from './session';

import * as _ from 'lodash';

@Injectable()
export class AuthService {
  constructor(private http: Http, private cookieService: CookieService) {}

  tokenKey = 'auth_token';

  saveToken(token: string) {
    this.cookieService.put(this.tokenKey, token);
  }

  removeToken() {
    this.cookieService.remove(this.tokenKey);
  }

  isLoggedIn() {
    return !_.isEmpty(this.getToken());
  }

  getToken() {
    return this.cookieService.get(this.tokenKey);
  }
};