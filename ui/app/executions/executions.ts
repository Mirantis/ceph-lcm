import * as _ from 'lodash';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from '../services/data';
import { Execution } from '../models';


@Component({
  templateUrl: './app/templates/executions.html',
})
export class ExecutionsComponent {
  executions: Execution[] = null;

  constructor(private data: DataService, private router: Router) {
    this.fetchData();
  }

  fetchData() {
    this.data.execution().findAll({})
      .then(
        (executions: Execution[]) => this.executions = executions,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  showExecutionLog(execution: Execution) {
    this.router.navigate(['/executions', execution.id]);
  }
}