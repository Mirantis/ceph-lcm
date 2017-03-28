/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { Injectable } from '@angular/core';
import { Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { SessionService } from './session';
import { DataService } from './data';
import { Token, User, Role } from '../models';
import globals = require('./globals');

import * as _ from 'lodash';
import * as $ from 'jquery';

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
          this.data.role().find(this.loggedUser.data.role_id)
            .then(
              (role: Role) => globals.loggedUserRole = role,
              (error: any) => this.data.handleResponseError(error)
            );

          var url = this.redirectUrl || '/';
          this.redirectUrl = null;
          this.router.navigate([url]);
          return token;
        },
        (error: any) => this.data.handleResponseError(error)
      )
      .catch((error: any) => this.data.handleResponseError(error));
  }

  logout(): Promise<void> {
    this.loggedUser = null;
    return this.data.token().destroy(null)
      .then(
        () => {
          this.session.removeToken();
          this.router.navigate(['/login']);
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  isLoggedIn(): boolean {
    return !_.isEmpty(this.session.getToken());
  }

  getLoggedUser(force: boolean = false): User {
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

  resetPassword(login: string): JQueryXHR {
    return this.data.postJSON('password_reset', {login});
  }

  checkPasswordResetToken(resetToken: string): JQueryXHR {
    return $.ajax(this.data.basePath + '/password_reset/' + resetToken);
  }

  updatePassword(resetToken: string, password: string): JQueryXHR {
    return this.data.postJSON('password_reset/' + resetToken, {password});
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
