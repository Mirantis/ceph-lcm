import { Component, ViewChild } from '@angular/core';
import { DataService, pagedResult } from '../services/data';
import { Filter, Pager } from '../directives';
import { Server } from '../models';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/servers.html',
})
export class ServersComponent {
  servers: Server[] = null;
  shownServerId: string = null;
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.server().findAll({
      filter: _.get(this.filter, 'query', {}),
      page: _.get(this.pager, 'page', 1)
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

  showConfiguration(server: Server) {
    this.shownServerId = this.shownServerId === server.id ?
      null : server.id;
  }
}