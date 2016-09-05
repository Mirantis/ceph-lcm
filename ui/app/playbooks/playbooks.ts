import { Component } from '@angular/core';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/playbooks.html',
})
export class PlaybooksComponent {
  playbooks: any[] = [];

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.playbook().findAll({})
      .then((playbooks: any) => this.playbooks = playbooks.playbooks);
  }
}