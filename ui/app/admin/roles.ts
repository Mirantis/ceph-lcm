/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { Component, Input, ViewChild } from '@angular/core';
import { AuthService } from '../services/auth';
import { DataService, pagedResult } from '../services/data';
import { User, Role, PermissionGroup } from '../models';
import { Modal } from '../directives';
import { WizardComponent } from '../wizard';
import { RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep } from './wizard_steps/index';
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
  }

  getRoleGroupPermissions(role: Role): string[] {
    let rolePermissionsGroup = _.find(role.data.permissions, {name: this.group.name});
    return rolePermissionsGroup ? rolePermissionsGroup.permissions : [];
  }

  getRolePermission(permission: string, role: Role) {
    return _.includes(this.getRoleGroupPermissions(role), permission);
  }
}

@Component({
  templateUrl: './app/templates/roles.html'
})
export class RolesComponent {
  @ViewChild(WizardComponent) wizard: WizardComponent;
  roles: Role[] = null;
  permissions: PermissionGroup[] = [];
  newRole: Role = new Role({data: {permissions: []}});
  roleSteps = [RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep];
  oldRoleName = '';

  constructor(
    private data: DataService,
    private modal: Modal,
    private auth: AuthService
  ) {
    this.fetchData();
    // Permissions are not going to change
    this.data.permission().findAll({})
      .then(
        (permissions: pagedResult) => this.permissions = permissions.items,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  fetchData() {
    this.data.role().findAll({})
      .then(
        (roles: pagedResult) => this.roles = roles.items,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  editRole(role: Role = null) {
    this.newRole = _.isNull(role) ? new Role({data: {permissions: []}}) : role.clone();
    this.wizard.init(this.newRole);
    this.modal.show();
    this.oldRoleName = '"' + this.newRole.data.name + '"';
  }

  deleteRole(role: Role = null) {
    this.data.role().destroy(role.id)
      .then(
        () => this.fetchData(),
        (error: any) => this.data.handleResponseError(error)
      );
  }

  save() {
    var savePromise: Promise<any>;
    if (this.newRole.id) {
      // Update role
      savePromise = this.data.role().postUpdate(this.newRole.id, this.newRole)
        .then(() => this.auth.invalidateUser());
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

