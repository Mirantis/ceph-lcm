import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { Cluster, Server, Playbook, PlaybookConfiguration, Execution } from '../models';
import { Record } from 'js-data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent {

  configurations: PlaybookConfiguration[] = null;
  clusters: Cluster[] = [];
  playbooks: Playbook[] = [];
  servers: Server[] = [];
  shownConfigurationId: string = null;
  configurationVersions: {[key: string]: PlaybookConfiguration[]} = {};
  error: any;

  constructor(
    private data: DataService,
    private modal: Modal,
    private router: Router
  ) {
    this.fetchData();
  }

  fetchData() {
    this.data.configuration().findAll({})
      .then(
        (configurations: PlaybookConfiguration[]) => this.configurations = configurations,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  editConfiguration(configuration: PlaybookConfiguration = null) {
    Promise.all([
      this.data.cluster().findAll({})
        .then((clusters: Cluster[]) => this.clusters = clusters),
      this.data.playbook().findAll({})
        .then((playbooks: Playbook[]) => this.playbooks = playbooks),
      this.data.server().findAll({})
        .then((servers: Server[]) => this.servers = servers)
    ]).catch((error: any) => this.data.handleResponseError(error));

    this.modal.show();
  }

  showVersions(configuration: PlaybookConfiguration) {
    this.shownConfigurationId = this.shownConfigurationId === configuration.id ?
      null : configuration.id;
  }

  getConfigurationVersions(configuration: PlaybookConfiguration) {
    if (!this.configurationVersions[configuration.id]) {
      this.data.configuration().getVersions(configuration.id)
        .then(
          (versions: PlaybookConfiguration[]) => {
            this.configurationVersions[configuration.id] = versions;
          },
          (error: any) => this.data.handleResponseError(error)
        );
      this.configurationVersions[configuration.id] = [];
    }
    return this.configurationVersions[configuration.id];
  }

  executeConfiguration(version: PlaybookConfiguration) {
    this.data.execution().postCreate(
      new Record({playbook_configuration: {id: version.id, version: version.version}})
    ). then(
      () => this.router.navigate(['/executions']),
      (error: any) => this.data.handleResponseError(error)
    );
  }
}