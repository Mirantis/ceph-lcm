import { Component } from '@angular/core';
import { DataService } from '../services/data';

import { Playbook } from '../models';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/playbooks.html',
})
export class PlaybooksComponent {
  playbooks: Playbook[] = null;

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.playbook().findAll({})
      .then(
        (playbooks: Playbook[]) => this.playbooks = playbooks,
        (error: any) => this.data.handleResponseError(error)
      );
  }
}