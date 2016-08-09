import {Injectable} from '@angular/core';
import {Http, Headers, Response} from '@angular/http';
import {AuthService} from './auth';
import {Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
// import {Observable} from 'rxjs/Observable';
import {DataService} from './data';

import * as _ from 'lodash';

@Injectable()
export class SessionService {

  constructor(
    private http: Http,
    private auth: AuthService,
    private data: DataService
  ) {}

  redirectUrl: string;

  login(email: string, password: string): Promise<any> {
    return this.data.getMapper('auth')
      .create({login: email, password: password})
      .then((result: Response) => {
        console.log('Result', result, result.model_data);
        this.auth.saveToken(result.id);
        let url = this.redirectUrl;
        this.redirectUrl = null;
        return url;
      }, (error) => {
        console.warn(error);
      })
  }

  logout(): Promise<any> {
    return this.data.getMapper('auth')
      .destroy(null)
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