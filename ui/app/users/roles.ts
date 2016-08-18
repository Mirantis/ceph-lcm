import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';

import { DataService } from '../services/data';
import { Modal } from '../bootstrap';
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
      <button class='btn btn-link btn-lg'>
        <span
          class="glyphicon"
          [ngClass]="getRolePermission(grouppee, role) ? 'glyphicon-ok text-success' : 'glyphicon-remove text-danger'"
          aria-hidden="true"></span>
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
    return _.includes(role[this.group], permission);
  }
}

@Component({
  template: `
<button (click)="createRole()" class="btn btn-success pull-right">Create Role</button>
<modal>
  <h4 class="modal-title">New Role</h4>
  <div class="modal-body">
    <form #newRoleForm="ngForm">
      <div class="form-group">
        <label for="roleName">Role Name</label>
        <input
          type="text"
          class="form-control"
          name="roleName"
          id="roleName"
          placeholder="Role Name"
          [(ngModel)]="newRole.name"
          required>
      </div>
      <div *ngFor="let group of permissions|keys">
        <h5>{{group}}</h5>
        <div class="checkbox" *ngFor="let permission of permissions|key:group">
          <label>
            <input
              type="checkbox"
              [name]="group"
              [value]="permission"
              [checked]="getGroupPermission(group, permission)"
              (click)="toggleGroupPermission(group, permission)"> {{permission}}
          </label>
        </div>
      </div>
     </form>
  </div>
  <div class="modal-footer">
    <button class="btn btn-default" (click)="modal.close()">Cancel</button>
    <button
      class="btn btn-success"
      (click)="save()"
      [disabled]="!newRoleForm.form.valid">Save changes</button>
  </div>
</modal>

<h3>Roles Permissions</h3>
<table class="roles table" *ngIf="roles.length">
  <thead>
    <tr>
      <th></th>
      <th *ngFor="let role of roles">{{role.data.name}}</th>
    </tr>
  </thead>
  <tbody PermissionsGroup
    *ngFor="let group of permissions|keys"
    [group]="group"
    [roles]="roles"
    [permissions]="permissions">
  </tbody>
</table>
`,
  directives: [PermissionsGroup, Modal]
})
export class RolesComponent {
  roles: any[] = [];
  permissions: Object = {};
  newRole: any = {permissions: {}};

  constructor(private data: DataService, private modal: Modal) {
    this.data.role().findAll({})
      .then((roles: any) => this.roles = roles.items);
    this.data.permissions().findAll({})
      .then((permissions: Object) => this.permissions = permissions);
  }

  createRole() {
    this.newRole = {permissions: {}};
    this.modal.show();
  }

  getGroupPermission(group: string, permission: string): boolean {
    return _.includes(_.get(this.newRole.permissions, group, []), permission);
  }

  toggleGroupPermission(group: string, permission: string) {
    var groupPermissions = _.get(this.newRole.permissions, group, []);
    if (this.getGroupPermission(group, permission)) {
      _.pull(groupPermissions, permission);
      if (_.isEmpty(groupPermissions)) {
        delete this.newRole.permissions[group];
        return;
      }
    } else {
      groupPermissions.push(permission);
    }
    this.newRole.permissions[group] = groupPermissions;
  }

  save() {
    this.modal.close();
  }
};

