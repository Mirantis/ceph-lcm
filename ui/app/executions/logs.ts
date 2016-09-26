import * as _ from 'lodash';
import { Component } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { Record } from 'js-data';
import { DataService } from '../services/data';
import { Execution, ExecutionStep } from '../models';

@Component({
  templateUrl: './app/templates/logs.html'
})
export class LogsComponent {
  execution: Execution = null;
  steps: ExecutionStep[] = [new ExecutionStep({})];
  poller: NodeJS.Timer;
  stopPolling: boolean = false;

  constructor (private data: DataService, private route: ActivatedRoute) {
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

  fetchData() {
    if (this.execution) {
      this.data.execution().getLogs(this.execution.id)
        .then((steps: ExecutionStep[]) => {
          this.steps = steps;
          if (!this.stopPolling) {
            this.poller = setTimeout(() => this.fetchData(), 5000);
          }
        })
        .catch((error: any) => this.data.handleResponseError(error));
    }
  }
}