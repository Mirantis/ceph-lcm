import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';

@Component({
  templateUrl: './app/templates/users.html',
  directives: [Modal]
})
export class UsersComponent {
  users: any[] = [];
  roles: any[] = [];
  newUser: any = {data: {}};

  constructor(private data: DataService, private modal: Modal) {
    this.data.user().findAll({})
      .then((users: any) => this.users = users.items);
    this.data.role().findAll({})
      .then((roles: any) => this.roles = roles.items);
  }

  editUser(user: any = null) {
    this.newUser = _.isNull(user) ? {data: {}} : user;
    this.modal.show();
  }
}