import { Component, Input } from '@angular/core';
import { DataService } from '../services/data';
import * as _ from 'lodash';

@Component({
  selector: '[PermissionsGroup]',
  template: `
  <tr>
      <th>{{group}}</th>
      <th [colSpan]='roles.length'></th>
  </tr>
  <tr *ngFor='let grouppee of getPermissions()'>
    <td>{{grouppee}}</td>
    <td *ngFor='let role of roles'>
      <button class='btn btn-link btn-lg' [innerHTML]='getRolePermission(grouppee, role)'>
      </button>
    </td>
  </tr>
`
})
export class PermissionsGroup {
  @Input() group: string;
  @Input() roles: any[];
  @Input() permissions: Object;

  getPermissions(): any[] {
    return this.permissions[this.group];
  }
  getRolePermission(permission: string, role: Object) {
    return _.includes(role[this.group], permission) ? 'V' : '&times;';
  }
}

@Component({
  template: `
<h3>Roles Permissions</h3>
<table class='roles table' *ngIf='roles.length'>
  <thead>
    <tr>
      <th></th>
      <th *ngFor='let role of roles'>{{role.data.name}}</th>
    </tr>
  </thead>
  <tbody PermissionsGroup
    *ngFor='let group of permissions|keys'
    [group]='group'
    [roles]='roles'
    [permissions]='permissions'>
  </tbody>
</table>
`,
  directives: [PermissionsGroup]
})
export class RolesComponent {
  roles: any[] = [];
  permissions: Object = {};
  constructor(private data: DataService) {
    this.data.role().findAll({})
      .then((roles: any) => this.roles = roles.items);
    this.data.permissions().findAll({})
      .then((permissions: Object) => this.permissions = permissions);
  }
};

