import {Injectable} from '@angular/core';
import {Http, Headers} from '@angular/http';
import {CookieService} from 'angular2-cookie/core';
import {Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
import {Observable} from 'rxjs/Observable';

import * as _ from 'lodash';

@Injectable()
export class AuthService {
  private loggedIn = false;

  constructor(private http: Http, private cookieService: CookieService) {}

  redirectUrl: string;

  login(email: string, password: string): Observable<any> {
    this.cookieService.put('auth_token', 'bla-bla-token');
    return Observable.empty();

    // let headers = new Headers();
    // headers.append('Content-Type', 'application/json');

    // return this.http
    //   .post(
    //     '/login',
    //     JSON.stringify({email, password}),
    //     {headers}
    //   )
    //   .map(res => res.json())
    //   .map((res) => {
    //     if (res.success) {
    //       this.cookieService.put('auth_token', res.auth_token);
    //     }
    //     return res.success;
    //   })
    //   .catch(this.handleError);
  }
  
  private handleError (error: any) {
    let errMsg = (error.message) ? error.message :
      error.status ? `${error.status} - ${error.statusText}` : 'Server error';
    console.error(errMsg);
    return Observable.throw(errMsg);
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
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    if (this.authService.isLoggedIn()) {return true;}
    this.authService.redirectUrl = state.url;
    this.router.navigate(['/login']);
    return false;

  }
};