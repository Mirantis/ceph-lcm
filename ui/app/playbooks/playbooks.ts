import { Component } from '@angular/core';
import { AuthService } from '../services/auth';
import { DataService } from '../services/data';
import { Playbook } from '../models';
import globals = require('../services/globals');

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/playbooks.html',
})
export class PlaybooksComponent {
  playbooks: Playbook[] = null;

  constructor(private auth: AuthService, private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.playbook().findAll({})
      .then(
        (playbooks: Playbook[]) => this.playbooks = playbooks,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  isPlaybookPermitted(playbook: Playbook) {
    if (!globals.loggedUserRole) {
      return false;
    }
    var playbooksPermissions = _.find(globals.loggedUserRole.data.permissions, {name: 'playbook'});
    return _.includes(playbooksPermissions.permissions, playbook.id);
  }
}