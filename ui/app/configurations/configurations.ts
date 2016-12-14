import * as _ from 'lodash';
import { Record } from 'js-data';
import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { Modal, Filter, Pager } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { BaseModel, Cluster, Server, Playbook, PlaybookConfiguration, Execution } from '../models';
import { WizardComponent } from './wizard';
import { WizardStepBase, NameAndClusterStep, PlaybookStep, HintsStep } from './wizard_steps';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent {
  model: PlaybookConfiguration = this.cleanModel();

  configurations: PlaybookConfiguration[] = null;
  clusters: Cluster[] = [];
  playbooks: Playbook[] = [];
  servers: Server[] = [];
  shownConfiguration: PlaybookConfiguration = null;
  configurationVersions: {[key: string]: PlaybookConfiguration[]} = {};
  @ViewChild(WizardComponent) wizard: WizardComponent;
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;

  configurationCreationSteps = [
    NameAndClusterStep,
    PlaybookStep,
    HintsStep
  ];


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

  cleanModel(): PlaybookConfiguration {
    return this.model = new PlaybookConfiguration({
      data: {
        name: '',
        server_ids: [],
        hints: []
      }
    });
  }

  editConfiguration(configuration: PlaybookConfiguration = null) {
    this.model = configuration ? configuration.clone() : this.cleanModel();
    // if (!configuration) {
    //     Promise.all([
    //       this.data.cluster().findAll({})
    //         .then((clusters: pagedResult) => this.clusters = clusters.items),
    //       this.data.playbook().findAll({})
    //         .then((playbooks: pagedResult) => this.playbooks = playbooks.items),
    //       this.data.server().findAll({})
    //         .then((servers: pagedResult) => this.servers = servers.items)
    //     ]).catch((error: any) => this.data.handleResponseError(error));
    // }
    this.wizard.init(configuration);
    this.modal.show();
  }

  save(model: BaseModel) {
    var savePromise: Promise<BaseModel>;
    if (model.id) {
      // Update configuration
      // model.data.configuration = JSON.parse(this.jsonConfiguration);
      savePromise = this.data.configuration().postUpdate(model.id, model);
    } else {
      // Create new configuration
      savePromise = this.data.configuration().postCreate(model);
    }
    return savePromise
      .then(
        (configuration: Object) => {
          // Seems jsdata returns the payload as a part of create response.
          // Unneeded values should be removed.
          let pureConfig = new BaseModel(
            _.omit(configuration, ['playbook_id', 'cluster_id', 'name', 'server_ids'])
          );
          this.wizard.init(pureConfig);
          this.refreshConfigurations();
        }
      )
      .catch(
        (error: any) => this.data.handleResponseError(error)
      );
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