import { Component } from '@angular/core';

import { DataService } from '../services/data';

@Component({
  template: `
<table class='roles table' *ngIf='roles.length'>
  <thead>
    <tr>
      <th></th>
      <th *ngFor='let role of roles'>{{role.data.name}}</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor='let permission of [1, 2, 3, 4]'>
      <th>{{permission}}</th>
      <td *ngFor='let role of roles'>&times;</td>
    </tr>
  </tbody>
</table>
`
})
export class RolesComponent {
  roles: any[] = [];
  constructor(private data: DataService) {
    this.data.role().findAll({})
      .then((roles: any) => this.roles = roles.items);
  }
};