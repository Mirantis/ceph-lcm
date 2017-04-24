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

import { Component, ViewChild } from '@angular/core';
import { Modal } from '../directives';
import { AuthService } from '../services/auth';
import { ErrorService } from '../services/error';
import { DataService, pagedResult } from '../services/data';
import { User, Role } from '../models';
import { WizardComponent } from '../wizard';
import { UserStep } from './wizard_steps/user';

import * as _ from 'lodash';

type roleIdsType = {[key: string]: Role};
type userVersionsType = {[key: string]: User[]};

@Component({
  templateUrl: './app/templates/users.html'
})
export class UsersComponent {
  @ViewChild(WizardComponent) wizard: WizardComponent;
  userSteps = [UserStep];
  users: User[] = null;
  userVersions: userVersionsType = {};
  roles: Role[] = [];
  roleIds: roleIdsType = {};
  newUser: User = new User({});
  shownUserId: string = null;
  pagedData: pagedResult = {} as pagedResult;
  canSeeRoles: boolean = false;

  constructor(
    private auth: AuthService,
    private data: DataService,
    private error: ErrorService,
    private modal: Modal
  ) {
    this.fetchData();
  }

  fetchData() {
    this.data.user().findAll({})
      .then(
        (users: pagedResult) => {
          this.users = users.items;
          this.pagedData = users;
        },
        (error: any) => this.data.handleResponseError(error)
       );

    this.auth.isAuthorizedTo('view_role')
      .then(canSeeRoles => {
        this.canSeeRoles = canSeeRoles;
        if (!canSeeRoles) return;

        this.data.role().findAll({})
          .then(
            (roles: pagedResult) => {
              this.roles = roles.items;
              this.roleIds = _.reduce(
                this.roles,
                (result: roleIdsType, role: Role) => {
                  result[role.id] = role;
                  return result;
                },
                {} as roleIdsType
              );
            },
            (error: any) => this.data.handleResponseError(error)
          );
      });
  }

  getRoleName(role_id: string): string {
    let role = this.roleIds[role_id];
    return role ? role.data.name : '-';
  }

  editUser(user: User = null) {
    this.newUser = _.isNull(user) ? new User({}) : user.clone();
    this.shownUserId = null;
    this.wizard.init(this.newUser);
    this.modal.show();
  }

  saveUser() {
    if (!this.canSeeRoles) {
      _.unset(this.newUser, 'data.role_id');
    }

    var savePromise: Promise<any>;
    if (this.newUser.id) {
      // Update existing user' data
      savePromise = this.data.user().postUpdate(this.newUser.id, this.newUser)
        .then(
          (user: User) => {
            if (this.newUser.id === this.auth.loggedUser.id) {
              this.auth.invalidateUser();
            }
            this.newUser = user;
          },
          (error: any) => this.data.handleResponseError(error)
        );
    } else {
      // Create new user
      savePromise = this.data.user().postCreate(this.newUser);
    }
    return savePromise
      .then(
        () => {
          this.modal.close();
          this.fetchData();
          if (this.newUser.id) {
            this.getUserVersions(this.newUser, true);
          }
        },
        (error: any) => this.data.handleResponseError(error)
      );
}

  deleteUser(user: User) {
    this.data.user().destroy(user.id)
      .then(() => {
        this.shownUserId = null;
        this.fetchData();
      });
  }

  resetUserPassword(user: User) {
    this.auth.resetPassword(user.data.login)
      .then(
        (data: any) => this.error.add(user.data.login, 'Password reset instructions have been sent'),
        (error: any) => this.data.handleResponseError(error)
      )
  }

  showUserData(user: any) {
    this.shownUserId = this.shownUserId === user.id ? null : user.id;
    this.newUser = _.isNull(this.shownUserId) ? new User({}) : user.clone();
  }

  getUserVersions(user: any, reread: boolean = false): User[] {
    if (!this.userVersions[user.id] || reread) {
      this.data.user().getVersions(user.id)
        .then(
          (versions: pagedResult) => {
            this.userVersions[user.id] = versions.items;
          },
          (error: any) => this.data.handleResponseError(error)
        );
      this.userVersions[user.id] = [];
    }
    return this.userVersions[user.id];
  }
}
