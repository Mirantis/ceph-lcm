import { Component, ViewChild } from '@angular/core';
import { DataService } from '../services/data';
import { Filter } from '../directives';
import { Server } from '../models';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/servers.html',
})
export class ServersComponent {
  servers: Server[] = null;
  shownServerId: string = null;
  configuration: string[][] = [
    ['name', 'fqdn', 'ip'], ['state', 'cluster_id']
  ];
  @ViewChild(Filter) filter: Filter;

  constructor(private data: DataService) {
    this.fetchData();
  }

  fetchData() {
    this.data.server().findAll({filter: _.get(this.filter, 'query', {})})
      .then((servers: Server[]) => this.servers = servers)
      .catch((error: any) => this.data.handleResponseError(error));
  }

  showVersions(server: Server) {
    this.shownServerId = this.shownServerId === server.id ?
      null : server.id;
  }
}