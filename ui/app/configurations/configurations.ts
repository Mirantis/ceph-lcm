import { Component, ViewChild } from '@angular/core';
import { NgSwitch, NgSwitchCase } from '@angular/common';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { Cluster, Server, Playbook, PlaybookConfiguration } from '../models';

import { WizardComponent } from './wizard';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent {
  @ViewChild(WizardComponent) wizard: WizardComponent;
  configurations: PlaybookConfiguration[] = null;
  clusters: Cluster[] = [];
  playbooks: Playbook[] = [];
  servers: Server[] = [];
  shownConfigurationId: string = null;
  configurationVersions: {[key: string]: PlaybookConfiguration[]} = {};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.configuration().findAll({})
      .then((configurations: PlaybookConfiguration[]) => this.configurations = configurations);
  }

  editConfiguration(configuration: PlaybookConfiguration = null) {
    this.data.cluster().findAll({})
      .then((clusters: any) => this.clusters = clusters);
    this.data.playbook().findAll({})
      .then((playbooks: any) => this.playbooks = playbooks);
    this.data.server().findAll({})
      .then((servers: any) => this.servers = servers);
    this.modal.show();
  }

  showVersions(configuration: PlaybookConfiguration) {
    this.shownConfigurationId = this.shownConfigurationId === configuration.id ?
      null : configuration.id;
  }

  getConfigurationVersions(configuration: PlaybookConfiguration) {
    if (!this.configurationVersions[configuration.id]) {
      this.data.configuration().getVersions(configuration.id)
        .then((versions: PlaybookConfiguration[]) => {
          this.configurationVersions[configuration.id] = versions;
        });
      this.configurationVersions[configuration.id] = [];
    }
    return this.configurationVersions[configuration.id];
  }
}