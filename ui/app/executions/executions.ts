import { Component } from '@angular/core';
import { DataService } from '../services/data';
import { Execution } from '../models';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/executions.html',
})
export class ExecutionsComponent {
  executions: Execution[] = null;

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.execution().findAll({})
      .then((executions: Execution[]) => this.executions = executions);
  }
}