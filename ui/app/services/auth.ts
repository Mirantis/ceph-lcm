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

import { Injectable, Directive, Input, ElementRef, EventEmitter } from '@angular/core';
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

  roleLock: Promise<Role> = null;
  userLock: Promise<User> = null;

  userDataUpdated = new EventEmitter();

  login(username: string, password: string): Promise<any> {
    return this.data.token()
      .create({username, password})
      .then(
        (token: Token) => {
          this.session.saveToken(token);

          this.loggedUser = token.data.user;
          return this.data.role().find('self')
            .then(
              (role: Role) => {
                globals.loggedUserRole = role;
                var url = this.redirectUrl || '/';
                this.redirectUrl = null;
                this.router.navigate([url]);
              },
              (error: any) => this.data.handleResponseError(error)
            );
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

  getCurrentRole(force: boolean = false): Promise<Role> {
    if (!this.isLoggedIn()) {
      return Promise.reject('User is not logged in');
    }
    if (globals.loggedUserRole && !force) {
      return Promise.resolve(globals.loggedUserRole);
    }
    if (!this.roleLock || force) {
      this.roleLock = this.data.role().find('self')
        .then(
          (role: Role) => {
            globals.loggedUserRole = role;
            this.userDataUpdated.emit();
            return role;
          },
          (error: any) => this.data.handleResponseError(error)
        )
        .then(role => {
            this.roleLock = null;
            return role;
          }
        )
    }
    return this.roleLock;
  }

  getLoggedUser(force: boolean = false): User {
    if (force || (this.isLoggedIn() && !this.loggedUser)) {
      if (!this.userLock) {
        this.userLock = this.data.user().find('self')
          .then(
            (user: User) => {
              this.loggedUser = user;
              this.getCurrentRole(force)
                .catch(error => this.data.handleResponseError(error));
            },
            error => this.data.handleResponseError(error)
          )
          .then(() => this.userLock = null);
      }
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

  isAuthorizedTo(access: string|string[]): Promise<boolean> {
    let restrictions = _.flatten([access]);
    if (_.isEmpty(restrictions)) {
      // Component is unrestricted - all logged users can see it
      return Promise.resolve(true);
    }
    return this.getCurrentRole()
      .then(
        (currentRole: Role) => {
          let apiPermissions = _.find(
            _.get(currentRole, 'data.permissions') as any[],
            {name: 'api'}
          );

          if (!apiPermissions) {
            // Role has no access to the api - cannot navigate internals
            return false;
          };

          // If component has restrictions they must intersect with the
          // active role's permissions to proceed
          return _.some(restrictions, (restrict: string) => {
            return _.includes(apiPermissions.permissions, restrict);
          });
        },
        error => this.data.handleResponseError(error)
      );
  }
}

@Injectable()
export class LoggedIn implements CanActivate {
  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Promise<boolean>|boolean {
    if (this.auth.isLoggedIn()) {
      let componentRestrictions = _.compact(
        _.flatten([_.get(route.routeConfig.data, 'restrictTo')])
      ) as string[];
      return this.auth.isAuthorizedTo(componentRestrictions);
    }
    this.auth.redirectUrl = state.url;
    this.router.navigate(['/login']);
    return false;
  }
};

@Directive({
  selector: '[shownFor]'
})
export class ShownFor {
  @Input() shownFor: string|string[];

  constructor(
    private auth: AuthService,
    private element: ElementRef
  ) {
    this.auth.userDataUpdated.subscribe(() => this.updateState());
  }

  updateState() {
    this.auth.isAuthorizedTo(this.shownFor)
      .then(isAllowed => this.element.nativeElement.style.display = isAllowed ? '' : 'none');
  }

  ngOnInit() {
    this.updateState();
  }
}
