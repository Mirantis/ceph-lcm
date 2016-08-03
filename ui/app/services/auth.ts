import {Injectable} from '@angular/core';
import {Http, Headers} from '@angular/http';
import {CookieService} from 'angular2-cookie/core';
import {Router, CanActivate} from '@angular/router';
import * as _ from 'lodash';

@Injectable()
export class AuthService {
  private loggedIn = false;

  constructor(private http: Http, private cookieService: CookieService) {}

  login(email: string, password: string) {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    return this.http
      .post(
        '/login',
        JSON.stringify({email, password}),
        {headers}
      )
      .map(res => res.json())
      .map((res) => {
        if (res.success) {
          this.cookieService.put('auth_token', res.auth_token);
        }
        return res.success;
      });
  }

  logout() {
    this.cookieService.remove('auth_token');
  }

  isLoggedIn() {
    return !_.isEmpty(this.cookieService.get('auth_token'));
  }
}

@Injectable()
export class LoggedIn implements CanActivate {
  constructor(private authService: AuthService) {}

  canActivate() {
    return this.authService.isLoggedIn();
  }
};