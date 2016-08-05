import {Injectable} from '@angular/core';
import {Http, Headers} from '@angular/http';
import {AuthService} from './auth';
import {Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
import {Observable} from 'rxjs/Observable';
import {BaseApiService} from './base';

import * as _ from 'lodash';

@Injectable()
export class SessionService {

  constructor(
    private http: Http,
    private auth: AuthService, private api: BaseApiService
  ) {}

  redirectUrl: string;

  login(email: string, password: string) {
    return this.api.get('/auth', {email, password})
      .catch(() => '5345353-34534732-343-3753211')  // TODO: handle
      .then(token => this.auth.saveToken(token));
  }

  logout() {
    return this.api.delete('/auth')
      .catch(() => true)  // TODO: handle
      .then(() => {
        this.auth.removeToken();
      });
  }
}

@Injectable()
export class LoggedIn implements CanActivate {
  constructor(
    private auth: AuthService,
    private session: SessionService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    if (this.auth.isLoggedIn()) {return true;}
    this.session.redirectUrl = state.url;
    this.router.navigate(['/login']);
    return false;

  }
};