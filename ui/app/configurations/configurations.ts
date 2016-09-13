import { Component, ViewChild } from '@angular/core';
import { NgSwitch, NgSwitchCase } from '@angular/common';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';

import { WizardComponent } from './wizard';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent {
  @ViewChild(WizardComponent) wizard: WizardComponent;
  configurations: any[] = null;
  clusters: any[] = [];
  playbooks: any[] = [];
  servers: any[] = [];
  shownConfigurationId: string = null;
  configurationVersions: {[key: string]: any[]} = {};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.configuration().findAll({})
      .then((configurations: any) => this.configurations = configurations.items);
  }

  editConfiguration(configuration: any = null) {
    this.data.cluster().findAll({})
      .then((clusters: any) => this.clusters = clusters.items);
    this.data.playbook().findAll({})
      .then((playbooks: any) => this.playbooks = playbooks.playbooks);
    this.data.server().findAll({})
      .then((servers: any) => this.servers = servers.items);
    this.modal.show();
  }

  showVersions(configuration: any) {
    this.shownConfigurationId = this.shownConfigurationId === configuration.id ?
      null : configuration.id;
  }

  getConfigurationVersions(configuration: any) {
    if (!this.configurationVersions[configuration.id]) {
      this.data.configuration().getVersions(configuration.id)
        .then((versions: any) => {
          this.configurationVersions[configuration.id] = versions.items;
        });
      this.configurationVersions[configuration.id] = [];
    }
    return this.configurationVersions[configuration.id];
  }
}