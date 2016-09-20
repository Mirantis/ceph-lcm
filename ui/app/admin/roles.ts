import { Component, Input } from '@angular/core';
import { DataService } from '../services/data';
import { User, Role, PermissionGroup } from '../models';
import { Modal } from '../bootstrap';
import * as _ from 'lodash';

type rolesPermissionGroupsType = {[key: string]: string[]};

@Component({
  selector: '[PermissionsGroup]',
  templateUrl: './app/templates/roles_permissions_group.html'
})
export class PermissionsGroup {
  @Input() group: PermissionGroup;
  @Input() roles: Role[];
  rolesPermissionGroups: rolesPermissionGroupsType = {};

  constructor() {
    this.rolesPermissionGroups = _.reduce(
      this.roles,
      (result: rolesPermissionGroupsType, role: Role) => {
        let rolePermissionsGroup = _.find(role.data.permissions, {name: this.group.name});
        result[role.id] = rolePermissionsGroup ? rolePermissionsGroup.permissions : [];
        return result;
      },
      {}
    ) as rolesPermissionGroupsType;
  }

  getRolePermission(permission: string, role: Role) {
    return _.includes(this.rolesPermissionGroups[role.id], permission);
  }
}

@Component({
  templateUrl: './app/templates/roles.html'
})
export class RolesComponent {
  roles: Role[] = null;
  permissions: [PermissionGroup] = [] as [PermissionGroup];
  newRole: Role = new Role({});
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
    // Permissions are not going to change
    this.data.permission().findAll({})
      .then(
        (permissions: [PermissionGroup]) => this.permissions = permissions,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  getPermissionsGroupByName(groupName: string, haystack: [PermissionGroup]): PermissionGroup {
    return _.find(haystack, {data: {name: groupName}})
      || new PermissionGroup({data: {name: groupName, permissions: []}})
  }

  fetchData() {
    this.data.role().findAll({})
      .then(
        (roles: Role[]) => this.roles = roles,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  editRole(role: Role = null) {
    this.newRole = _.isNull(role) ? new Role({}) : role.clone();
    this.modal.show();
  }

  deleteRole(role: Role = null) {
    this.data.role().destroy(role.id)
      .then(
        () => this.fetchData(),
        (error: any) => this.data.handleResponseError(error)
      );
  }

  getGroupPermission(group: PermissionGroup, permission: string): boolean {
    return _.includes(group.permissions, permission);
  }

  toggleGroupPermission(group: PermissionGroup, permission: string) {
    let groupIndex = _.findIndex(this.newRole.data.permissions, {name: group.name});
    let groupPermissions = this.newRole.data.permissions[groupIndex];

    if (this.getGroupPermission(group, permission)) {
      _.pull(groupPermissions.permissions, permission);
      if (_.isEmpty(groupPermissions.permissions)) {
        this.newRole.data.permissions = _.remove(
          this.newRole.data.permissions,
          (roleGroup) => roleGroup.name === group.name
        ) as [PermissionGroup];
        return;
      }
    } else {
      groupPermissions.permissions.push(permission);
    }
    this.newRole.data.permissions[groupIndex] = groupPermissions;
  }

  save() {
    this.error = null;
    var savePromise: Promise<any>;
    if (this.newRole.id) {
      // Update role
      savePromise = this.data.role().postUpdate(this.newRole.id, this.newRole);
    } else {
      // Create new role
      savePromise = this.data.role().postCreate(this.newRole);
    }
    return savePromise
      .then(
        () => {
          this.modal.close();
          this.fetchData();
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }
};

