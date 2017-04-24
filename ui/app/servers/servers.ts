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

import { Component, ViewChild, OnInit } from '@angular/core';
import { DataService, pagedResult } from '../services/data';
import { Pager } from '../directives';
import { Filter } from '../filter';
import { Server } from '../models';
import { Router, ActivatedRoute } from '@angular/router';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/servers.html'
})
export class ServersComponent implements OnInit {
  servers: Server[] = null;
  shownServerId: string = null;
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  constructor(
    private data: DataService,
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) {
    this.fetchData();
  }

  ngOnInit() {
    this.activatedRoute
      .fragment
      .subscribe((id: string) => {
        this.shownServerId = id;
      });
  }

  fetchData(page: number = 1) {
    this.data.server().findAll({
      filter: _.get(this.filter, 'query', {}),
      page
    })
      .then((servers: pagedResult) => {
        this.servers = servers.items;
        this.pagedData = servers;
      })
      .catch((error: any) => this.data.handleResponseError(error));
  }

  getKeyHalfsets(server: Server) {
    let keys = _.keys(server.data.facts).sort();
    return _.chunk(keys, Math.ceil(keys.length / 2));
  }
}
