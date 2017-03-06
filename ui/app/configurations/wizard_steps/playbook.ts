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
import globals = require('../../services/globals');
import { Component } from '@angular/core';
import { WizardStepBase } from '../../wizard_step';
import { DataService, pagedResult } from '../../services/data';
import { WizardService } from '../../services/wizard';
import { Playbook, PermissionGroup } from '../../models';

// Playbook selection
@Component({
  templateUrl: './app/templates/wizard_steps/playbook.html'
})
export class PlaybookStep extends WizardStepBase {
  playbooks: Playbook[] = [];

  public get selectedPlaybook(): Playbook {
    return this.getSharedData('selectedPlaybook');
  }
  public set selectedPlaybook(playbook: Playbook) {
    this.setSharedData('selectedPlaybook', playbook);
  }

  init() {
    this.selectedPlaybook = null;
    this.initModelProperty('data.playbook_id', '');
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }

  fetchData() {
    return this.data.playbook().getAll()
      .then((playbooks: pagedResult) => this.playbooks = playbooks.items);
  }

  isShownInDeck() {
    return !_.get(this.model, 'id');
  }

  isValid() {
    return !!_.get(this.model, 'data.playbook_id');
  }

  getAllowedPlaybooks(): Playbook[] {
    if (!globals.loggedUserRole) {
      return [];
    }
    var playbooksPermissions = _.find(
      globals.loggedUserRole.data.permissions,
      {name: 'playbook'}
    ) || new PermissionGroup();
    return _.filter(
      this.playbooks, (playbook) => _.includes(playbooksPermissions.permissions, playbook.id)
    );
  }

  selectPlaybook(playbook: Playbook) {
    if (!this.selectedPlaybook || this.selectedPlaybook.id !== playbook.id) {
      this.selectedPlaybook = playbook;
      this.model.data.hints = playbook.hints;
      this.model.data.playbook_id = playbook.id;
      this.model.data.server_ids = [];
    }
  }
}
