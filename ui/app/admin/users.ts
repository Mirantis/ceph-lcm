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
          (result, role) => {
            result[role.data.name] = role;
            return result;
          },
          {}
        )
      });
  }

  editUser(user: any = null) {
    this.newUser = _.isNull(user) ? {data: {}} : user;
    this.modal.show();
  }

  save() {
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

  showUserData(user: any) {
    this.shownUserId = this.shownUserId === user.id ? null : user.id;
  }


}