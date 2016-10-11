import { Injectable } from '@angular/core';
import { Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { SessionService } from './session';
import { DataService } from './data';
import { Token, User, Role } from '../models';
import globals = require('./globals');

import * as _ from 'lodash';

@Injectable()
export class AuthService {
  constructor(
    private session: SessionService,
    private data: DataService,
    private router: Router
  ) {}

  redirectUrl: string;
  public loggedUser: User = null;
  public loggedUserRole: Role = null;

  login(username: string, password: string): Promise<Token> {
    return this.data.token()
      .create({username, password})
      .then(
        (token: Token) => {
          this.session.saveToken(token);

          this.loggedUser = token.data.user;

          var url = this.redirectUrl || '/';
          this.redirectUrl = null;
          this.router.navigate([url]);
          return token;
        }
      )
      .catch((error: any) => this.data.handleResponseError(error));
  }

  logout(): Promise<void> {
    this.session.removeToken();
    this.loggedUser = null;
    return this.data.token().destroy(null)
      .then(
        () => {
          this.router.navigate(['/login']);
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  isLoggedIn(): boolean {
    return !_.isEmpty(this.session.getToken());
  }

  getLoggedUser(force: boolean): User {
    if (force || (this.isLoggedIn() && !this.loggedUser)) {
      this.data.user().find(this.session.getLoggedUserId())
        .then(
          (user: User) => {
            this.loggedUser = user;
            this.data.role().find(user.data.role_id)
              .then((role: Role) => globals.loggedUserRole = role);
          },
          (error: any) => this.data.handleResponseError(error)
        );
    }
    return this.loggedUser;
  }

  invalidateUser() {
    this.getLoggedUser(true);
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