import { Component } from '@angular/core';

import { DataService } from '../services/data';

@Component({
  template: `
<table class='users table' *ngIf='users.length'>
  <thead>
    <tr>
      <th>Login</th>
      <th>Full Name</th>
      <th width='1%'>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor='let user of users'>
      <td>{{user.data.login}}</td>
      <td>{{user.data.full_name}}</td>
      <td><button (click)='edit(user.id)' class='btn btn-sm'>Edit</button></td>
    </tr>
  </tbody>
</table>
  `
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