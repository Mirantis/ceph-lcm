import { Component } from '@angular/core';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/servers.html',
})
export class ServersComponent {
  servers: any[] = null;
  shownServerId: any = null;
  configuration: any [] = [
    ['name', 'fqdn', 'ip'], ['state', 'cluster_id']
  ];

  constructor(private data: DataService) {
    console.log(this.servers);
    this.fetchData();
  }

  fetchData() {
    this.data.server().findAll({})
      .then((servers: any) => this.servers = servers.items);
  }

  showVersions(server: any) {
    this.shownServerId = this.shownServerId === server.id ?
      null : server.id;
  }
}