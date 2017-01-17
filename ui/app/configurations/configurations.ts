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
import { Record } from 'js-data';
import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { Modal, Filter, Pager } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { BaseModel, Cluster, Server, Playbook, PlaybookConfiguration, Execution } from '../models';
import { WizardComponent } from '../wizard';
import { NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep } from './wizard_steps/index';

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

  configurationSteps = [
    NameAndClusterStep,
    PlaybookStep,
    HintsStep,
    ServersStep,
    JsonConfigurationStep
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
    return new PlaybookConfiguration({});
  }

  editConfiguration(configuration: PlaybookConfiguration = null, isReadOnly = false) {
    this.model = configuration ? configuration.clone() : this.cleanModel();
    this.wizard.init(this.model, isReadOnly);
    this.modal.show();
  }

  save(model: BaseModel) {
    let savePromise: Promise<BaseModel>;
    let shouldClose = false;
    if (model.id) {
      // Update configuration
      savePromise = this.data.configuration().postUpdate(model.id, model);
      shouldClose = true;
    } else {
      // Create new configuration
      // Update and create calls expect different set of parameters
      // thus some should be omitted
      _.unset(model, 'data.configuration');
      savePromise = this.data.configuration().postCreate(model);
    }
    return savePromise
      .then(
        (configuration: Object) => {
          // Seems jsdata returns the payload as a part of create response.
          // Unneeded values should be removed.
          let pureConfig = new BaseModel(
            _.omit(configuration, ['playbook_id', 'cluster_id', 'name', 'server_ids', 'hints'])
          );
          this.model = pureConfig;
          this.wizard.init(this.model);
          this.refreshConfigurations();
          if (shouldClose) {
            this.modal.close();
          }
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
