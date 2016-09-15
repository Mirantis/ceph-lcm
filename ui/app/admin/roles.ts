import { Component, Input } from '@angular/core';
import { DataService } from '../services/data';
import { User, Role, Permissions } from '../models';
import { Modal } from '../bootstrap';
import * as _ from 'lodash';

@Component({
  selector: '[PermissionsGroup]',
  templateUrl: './app/templates/roles_permissions_group.html'
})
export class PermissionsGroup {
  @Input() group: string;
  @Input() roles: Role[];
  @Input() permissions: Permissions;

  getPermissions(): string[] {
    return this.permissions[this.group];
  }
  getRolePermission(permission: string, role: Role) {
    return _.includes(role.data.permissions[this.group], permission);
  }
}

@Component({
  templateUrl: './app/templates/roles.html'
})
export class RolesComponent {
  roles: Role[] = null;
  permissions: Permissions = {} as Permissions;
  newRole: Role = new Role({});
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
    // Permissions are not going to change
    this.data.permissions().findAll({})
      .then((permissions: Permissions) => this.permissions = permissions);
  }

  fetchData() {
    this.data.role().findAll({})
      .then((roles: Role[]) => this.roles = roles);
  }

  editRole(role: Role = null) {
    this.newRole = _.isNull(role) ? new Role({}) : role.clone();
    this.modal.show();
  }

  deleteRole(role: Role = null) {
    this.data.role().destroy(role.id)
      .then(() => this.fetchData());
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

