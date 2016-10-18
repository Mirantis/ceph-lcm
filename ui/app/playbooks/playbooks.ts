import { Component, ViewChild } from '@angular/core';
import { AuthService } from '../services/auth';
import { DataService, pagedResult } from '../services/data';
import { Playbook } from '../models';
import { Pager } from '../directives';
import globals = require('../services/globals');

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/playbooks.html',
})
export class PlaybooksComponent {
  playbooks: Playbook[] = null;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  constructor(private auth: AuthService, private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.playbook().findAll({
      page: _.get(this.pager, 'page', 1)
    })
      .then(
        (playbooks: pagedResult) => {
          this.playbooks = playbooks.items;
          this.pagedData = playbooks;
        },
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