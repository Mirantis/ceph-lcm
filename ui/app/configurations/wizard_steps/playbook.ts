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
    return this.data.playbook().findAll({})
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