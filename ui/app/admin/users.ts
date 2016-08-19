import { Component } from '@angular/core';

import { DataService } from '../services/data';

@Component({
  templateUrl: './app/templates/users.html'
})
export class UsersComponent {
  users: any[] = [];
  constructor(private data: DataService) {
    this.data.user().findAll({})
      .then((users: any) => this.users = users.items);
  }

  edit(userId: string) {
  }
}