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

  fetchData(page: number = 1) {
    this.data.playbook().findAll({
      page
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
