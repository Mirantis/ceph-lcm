import * as _ from 'lodash';
import { Component, ViewChild } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { Record } from 'js-data';
import { ErrorService } from '../services/error';
import { DataService, pagedResult } from '../services/data';
import { Execution, ExecutionStep } from '../models';
import { Filter, Criterion, Pager } from '../directives';

@Component({
  templateUrl: './app/templates/logs.html'
})
export class LogsComponent {
  execution: Execution = null;
  steps: ExecutionStep[] = [];
  poller: NodeJS.Timer;
  stopPolling: boolean = false;
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;
  logFileDownloading = false;

  constructor (
    private data: DataService,
    private error: ErrorService,
    private route: ActivatedRoute
  ) {
    this.poller = setTimeout(() => this.fetchData(), 5000);
  }

  ngOnInit() {
    this.data.execution().find(this.route.snapshot.params['execution_id'])
      .then((exectution: Execution) => {
        this.execution = exectution;
        this.fetchData();
      })
      .catch((error: any) => this.data.handleResponseError(error));
  }

  ngOnDestroy() {
    this.stopPolling = true;
  }

  saveLogFile() {
    if (this.execution) {
      this.data.downloadExecutionLog(this.execution.id)
        .done(() => this.logFileDownloading = false)
        .fail((error: any) => this.data.handleResponseError(error));
      this.logFileDownloading = true;
    }
  }

  fetchData() {
    if (this.execution) {
      this.data.execution().getLogs(
        this.execution.id, {
          filter: _.get(this.filter, 'query', {}),
          page: _.get(this.pager, 'page', 1)
        }
      )
        .then((steps: pagedResult) => {
          this.steps = steps.items;
          this.pagedData = steps;
          if (!this.stopPolling) {
            this.poller = setTimeout(() => this.fetchData(), 5000);
          }
        })
        .catch((error: any) => this.data.handleResponseError(error));
    }
  }
}