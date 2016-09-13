import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/users.html'
})
export class UsersComponent {
  users: any[] = null;
  roles: any[] = [];
  rolesNames: Object = {};
  newUser: any = {data: {}};
  error: any;
  shownUserId: any = null;
  usersVersions: {[key: string]: any[]} = {};

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.user().findAll({})
      .then((users: any) => this.users = users.items);
    this.data.role().findAll({})
      .then((roles: any) => {
        this.roles = roles.items;
        this.rolesNames = _.reduce(
          this.roles,
          (result: any[], role: any) => {
            result[role.data.name] = role;
            return result;
          },
          {}
        )
      });
  }

  editUser(user: any = null) {
    this.newUser = _.isNull(user) ? {data: {}} : _.cloneDeep(user);
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

  deleteUser(user: any) {
    this.data.user().destroy(user.id)
      .then(() => {
        this.shownUserId = null;
        this.fetchData();
      });
  }

  showUserData(user: any) {
    this.shownUserId = this.shownUserId === user.id ? null : user.id;
    this.newUser = _.isNull(this.shownUserId) ? {data: {}} : _.cloneDeep(user);
  }

  getUserVersions(user: any): any[] {
    if (!this.usersVersions[user.id]) {
      this.data.user().getVersions(user.id)
        .then((versions: any) => {
          this.usersVersions[user.id] = versions.items;
        });
      this.usersVersions[user.id] = [];
    }
    return this.usersVersions[user.id];
  }

}