import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { User, Role } from '../models';

import * as _ from 'lodash';

type roleNamesType = {[key: string]: Role};
type userVersionsType = {[key: string]: User[]};

@Component({
  templateUrl: './app/templates/users.html'
})
export class UsersComponent {
  users: User[] = null;
  userVersions: userVersionsType = {};
  roles: Role[] = [];
  roleNames: roleNamesType = {};
  newUser: User = new User({});
  error: any;
  shownUserId: string = null;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.user().findAll({})
      .then((users: User[]) => this.users = users);
    this.data.role().findAll({})
      .then((roles: Role[]) => {
        this.roles = roles;
        this.roleNames = _.reduce(
          this.roles,
          (result: roleNamesType, role: Role) => {
            result[role.data.name] = role;
            return result;
          },
          {} as roleNamesType
        )
      });
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
      savePromise = this.data.user().update(this.newUser.id, this.newUser);
    } else {
      // Create new user
      savePromise = this.data.user().create(this.newUser);
    }
    return savePromise
      .then(
        () => {
          this.modal.close();
          this.fetchData();
        },
        (error) => {this.error = error}
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

  getUserVersions(user: any): User[] {
    if (!this.userVersions[user.id]) {
      this.data.user().getVersions(user.id)
        .then((versions: User[]) => {
          this.userVersions[user.id] = versions;
        });
      this.userVersions[user.id] = [];
    }
    return this.userVersions[user.id];
  }

}