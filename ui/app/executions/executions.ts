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
