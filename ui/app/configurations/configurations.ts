import * as _ from 'lodash';
import { Record } from 'js-data';
import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { Modal, Filter, Pager } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { Cluster, Server, Playbook, PlaybookConfiguration, Execution } from '../models';
import { WizardComponent } from './wizard';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent {

  configurations: PlaybookConfiguration[] = null;
  clusters: Cluster[] = [];
  playbooks: Playbook[] = [];
  servers: Server[] = [];
  shownConfiguration: PlaybookConfiguration = null;
  configurationVersions: {[key: string]: PlaybookConfiguration[]} = {};
  clone: PlaybookConfiguration = null;
  @ViewChild(WizardComponent) wizard: WizardComponent;
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  constructor(
    private data: DataService,
    private modal: Modal,
    private router: Router
  ) {
    this.fetchData();
    this.data.playbook().findAll({})
      .then((playbooks: pagedResult) => {
        this.playbooks = playbooks.items;
      })
  }

  getPlaybooksForFilter(): Object[] {
    return _.map(this.playbooks, (playbook: Playbook) => {
      return [playbook.name, playbook.id];
    });
  }

  fetchData(): Promise<any> {
    return this.data.configuration().findAll({
      filter: _.get(this.filter, 'query', {}),
      page: _.get(this.pager, 'page', 1)
    })
      .then(
        (configurations: pagedResult) => {
          this.configurations = configurations.items;
          this.pagedData = configurations;
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  editConfiguration(configuration: PlaybookConfiguration = null, readonly = false) {
    this.clone = configuration;
    if (!configuration) {
        Promise.all([
          this.data.cluster().findAll({})
            .then((clusters: pagedResult) => this.clusters = clusters.items),
          this.data.playbook().findAll({})
            .then((playbooks: pagedResult) => this.playbooks = playbooks.items),
          this.data.server().findAll({})
            .then((servers: pagedResult) => this.servers = servers.items)
        ]).catch((error: any) => this.data.handleResponseError(error));
    }
    this.wizard.init(configuration, readonly);
    this.modal.show();
  }

  refreshConfigurations() {
    if (this.shownConfiguration) {
      this.getConfigurationVersions(this.shownConfiguration, true);
    } else {
      this.fetchData();
    }
  }

  isCurrent(configuration: PlaybookConfiguration): boolean {
    return this.shownConfiguration && this.shownConfiguration.id === configuration.id;
  }

  showVersions(configuration: PlaybookConfiguration) {
    this.shownConfiguration = this.isCurrent(configuration) ? null : configuration;
  }

  getConfigurationVersions(configuration: PlaybookConfiguration, reread: boolean = false) {
    if (!this.configurationVersions[configuration.id] || reread) {
      this.configurationVersions[configuration.id] = [];
      this.data.configuration().getVersions(configuration.id)
        .then(
          (versions: pagedResult) => {
            this.configurationVersions[configuration.id] = versions.items;
          },
          (error: any) => this.data.handleResponseError(error)
        );
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