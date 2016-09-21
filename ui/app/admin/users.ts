import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
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
  error: any;
  shownUserId: string = null;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.user().findAll({})
      .then(
        (users: User[]) => this.users = users,
        (error) => this.data.handleResponseError(error)
       );
    this.data.role().findAll({})
      .then(
        (roles: Role[]) => {
          this.roles = roles;
          this.roleIds = _.reduce(
            this.roles,
            (result: roleIdsType, role: Role) => {
              result[role.id] = role;
              return result;
            },
            {} as roleIdsType
          );
        },
        (error) => this.data.handleResponseError(error)
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
    this.error = null;
    var savePromise: Promise<any>;
    if (this.newUser.id) {
      // Update user
      savePromise = this.data.user().postUpdate(this.newUser.id, this.newUser);
    } else {
      // Create new user
      savePromise = this.data.user().postCreate(this.newUser);
    }
    return savePromise
      .then(
        () => {
          this.modal.close();
          this.fetchData();
          this.getUserVersions(this.newUser, true);
        },
        (error) => this.data.handleResponseError(error)
      );
  }

  deleteUser(user: User) {
    this.data.user().destroy(user.id)
      .then(() => {
        this.shownUserId = null;
        this.fetchData();
      });
  }

  showUserData(user: any) {
    this.shownUserId = this.shownUserId === user.id ? null : user.id;
    this.newUser = _.isNull(this.shownUserId) ? new User({}) : user.clone();
  }

  getUserVersions(user: any, reread: boolean = false): User[] {
    if (!this.userVersions[user.id] || reread) {
      this.data.user().getVersions(user.id)
        .then(
          (versions: User[]) => {
            this.userVersions[user.id] = versions;
          },
          (error: any) => this.data.handleResponseError(error)
        );
      this.userVersions[user.id] = [];
    }
    return this.userVersions[user.id];
  }
}