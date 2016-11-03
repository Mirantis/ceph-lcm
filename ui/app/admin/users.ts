import { Component } from '@angular/core';
import { Modal } from '../directives';
import { AuthService } from '../services/auth';
import { ErrorService } from '../services/error';
import { DataService, pagedResult } from '../services/data';
import { User, Role } from '../models';

import * as _ from 'lodash';

type roleIdsType = {[key: string]: Role};
type userVersionsType = {[key: string]: User[]};

@Component({
  templateUrl: './app/templates/users.html'
})
export class UsersComponent {
  users: User[] = null;
  userVersions: userVersionsType = {};
  roles: Role[] = [];
  roleIds: roleIdsType = {};
  newUser: User = new User({});
  shownUserId: string = null;
  pagedData: pagedResult = {} as pagedResult;

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
  }

  getRoleName(role_id: string): string {
    let role = this.roleIds[role_id];
    return role ? role.data.name : '-';
  }

  editUser(user: User = null) {
    this.newUser = _.isNull(user) ? new User({}) : user.clone();
    this.shownUserId = null;
    this.modal.show();
  }

  saveUser() {
    var savePromise: Promise<any>;
    if (this.newUser.id) {
      // Update existing user' data
      savePromise = this.data.user().postUpdate(this.newUser.id, this.newUser)
        .then((user: User) => {
          if (this.newUser.id === this.auth.loggedUser.id) {
            this.auth.invalidateUser();
          }
          this.newUser = user;
        });
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
        }
      )
      .catch(
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