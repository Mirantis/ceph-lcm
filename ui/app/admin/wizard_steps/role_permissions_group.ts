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

import * as _ from 'lodash';
import { Component } from '@angular/core';
import { WizardStepBase } from '../../wizard_step';
import { WizardService } from '../../services/wizard';
import { DataService, pagedResult } from '../../services/data';
import { PermissionGroup } from '../../models';

// Role name adjustment
class RolePermissionsGroupStep extends WizardStepBase {
  protected groupName = '';
  allGroupPermissions: PermissionGroup = null;

  public get modelGroupPermissions(): string[] {
    let group: PermissionGroup = _.find(this.model.data.permissions, {name: this.groupName}) as PermissionGroup;
    if (!group) {
      group = {name: this.groupName, permissions: []} as PermissionGroup;
      this.model.data.permissions.push(group);
    }
    return group.permissions;
  }

  init() {
    this.initModelProperty('data.permissions', []);
  }

  fetchData() {
    return this.data.permission().findAll({})
      .then(
        (permissions: pagedResult) => {
          this.allGroupPermissions = _.find(permissions.items, {name: this.groupName});
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  getGroupPermission(permission: string): boolean {
    return _.includes(this.modelGroupPermissions, permission);
  }

  toggleGroupPermission(permission: string) {
    let groupPermissions = this.modelGroupPermissions;

    if (_.includes(groupPermissions, permission)) {
      _.pull(groupPermissions, permission);
    } else {
      groupPermissions.push(permission);
    }
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }
}

@Component({
  templateUrl: './app/templates/wizard_steps/role_permissions_group.html'
})
export class RoleApiPermissionsStep extends RolePermissionsGroupStep {
  protected groupName = 'api';

  constructor(wizard: WizardService, data: DataService) {
    super(wizard, data);
  }
}

@Component({
  templateUrl: './app/templates/wizard_steps/role_permissions_group.html'
})
export class RolePlaybookPermissionsStep extends RolePermissionsGroupStep {
  protected groupName = 'playbook';

  constructor(wizard: WizardService, data: DataService) {
    super(wizard, data);
  }
}