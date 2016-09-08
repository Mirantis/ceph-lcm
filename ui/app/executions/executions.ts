import { Component } from '@angular/core';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/executions.html',
})
export class ExecutionsComponent {
  executions: any[] = null;

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.execution().findAll({})
      .then((executions: any) => this.executions = executions.items);
  }
}