import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';

import { DataService } from '../services/data';
import { Modal } from '../bootstrap';
import * as _ from 'lodash';

@Component({
  selector: '[PermissionsGroup]',
  templateUrl: './app/templates/roles_permissions_group.html'
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
  templateUrl: './app/templates/roles.html',
  directives: [PermissionsGroup]
})
export class RolesComponent {
  roles: any[] = [];
  permissions: Object = {};
  newRole: any = {data: {permissions: {}}};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
    // Permissions are not going to change
    this.data.permissions().findAll({})
      .then((permissions: Object) => this.permissions = permissions);
  }

  fetchData() {
    this.data.role().findAll({})
      .then((roles: any) => this.roles = roles.items);
  }

  editRole(role: any = null) {
    this.newRole = _.isNull(role) ? {data: {permissions: {}}} : role;
    this.modal.show();
  }

  getGroupPermission(group: string, permission: string): boolean {
    return _.includes(_.get(this.newRole.data.permissions, group, []), permission);
  }

  toggleGroupPermission(group: string, permission: string) {
    var groupPermissions = _.get(this.newRole.data.permissions, group, []);
    if (this.getGroupPermission(group, permission)) {
      _.pull(groupPermissions, permission);
      if (_.isEmpty(groupPermissions)) {
        delete this.newRole.data.permissions[group];
        return;
      }
    } else {
      groupPermissions.push(permission);
    }
    this.newRole.data.permissions[group] = groupPermissions;
  }

  save() {
    this.error = null;
    var savePromise: Promise<any>;
    if (this.newRole.id) {
      // Update role
      savePromise = this.data.role().update(this.newRole.id, this.newRole);
    } else {
      // Create new role
      savePromise = this.data.role().create(this.newRole);
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
};

