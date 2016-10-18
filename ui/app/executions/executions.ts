import * as _ from 'lodash';
import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { DataService, pagedResult } from '../services/data';
import { Execution } from '../models';
import { Pager } from '../directives';


@Component({
  templateUrl: './app/templates/executions.html',
})
export class ExecutionsComponent {
  executions: Execution[] = null;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  constructor(private data: DataService, private router: Router) {
    this.fetchData();
  }

  fetchData() {
    this.data.execution().findAll({
      page: _.get(this.pager, 'page', 1)
    })
      .then(
        (executions: pagedResult) => {
          this.executions = executions.items;
          this.pagedData = executions;
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  showExecutionLog(execution: Execution) {
    this.router.navigate(['/executions', execution.id]);
  }
}