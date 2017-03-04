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

  fetchData(page: number = 1) {
    if (this.execution) {
      this.data.execution().find(this.execution.id)
        .then((execution: Execution) => this.execution = execution);

      this.data.execution().getLogs(
        this.execution.id, {
          filter: _.get(this.filter, 'query', {}),
          page
        }
      )
        .then((steps: pagedResult) => {
          this.steps = steps.items;
          this.pagedData = steps;
          if (!this.stopPolling && this.execution.data.state === 'Started') {
            this.poller = setTimeout(() => this.fetchData(), 5000);
          }
        })
        .catch((error: any) => this.data.handleResponseError(error));
    }
  }
}
