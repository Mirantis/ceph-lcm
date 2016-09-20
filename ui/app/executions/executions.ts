import * as _ from 'lodash';
import { Component } from '@angular/core';
import { DataService } from '../services/data';
import { Execution } from '../models';


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
      .then(
        (executions: Execution[]) => this.executions = executions,
        (error: any) => this.data.handleResponseError(error)
      );
  }
}