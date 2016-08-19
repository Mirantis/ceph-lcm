import {Injectable} from '@angular/core';
import {Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot} from '@angular/router';
import {SessionService} from './session';
import {DataService} from './data';

import * as _ from 'lodash';

@Injectable()
export class AuthService {
  constructor(
    private session: SessionService,
    private data: DataService,
    private router: Router
  ) {}

  redirectUrl: string;
  loggedUser: any = null;

  login(email: string, password: string): Promise<any> {
    return this.data.token()
      .create({login: email, password: password})
      .then((token: any) => {
        this.session.saveToken(token);

        this.getLoggedUser();

        var url = this.redirectUrl || '/dashboard';
        this.redirectUrl = null;
        this.router.navigate([url]);
      }, (error: any) => {
        console.warn(error);
      })
  }

  logout(): Promise<any> {
    this.session.removeToken();
    this.loggedUser = null;
    return this.data.token().destroy(null)
      .then(() => this.router.navigate(['/login']));
  }

  isLoggedIn() {
    return !_.isEmpty(this.session.getToken());
  }

  getLoggedUser() {
    if (this.isLoggedIn() && !this.loggedUser) {
      this.loggedUser = this.data.user().find(this.session.getLoggedUserId())
        .then((user: any) => {
          this.loggedUser = user;

          return this.loggedUser;
        });
    }
    return this.loggedUser;
  }
}


@Injectable()
export class LoggedIn implements CanActivate {
  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    if (this.auth.isLoggedIn()) {
      return true;
    }
    this.auth.redirectUrl = state.url;
    this.router.navigate(['/login']);
    return false;
  }
};