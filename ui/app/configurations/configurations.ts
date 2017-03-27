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
import { Component, ViewChild, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Modal } from '../directives';
import { Filter } from '../filter';
import { DataService, pagedResult } from '../services/data';
import { BaseModel, Cluster, Server, Playbook, PlaybookConfiguration, Execution } from '../models';
import { WizardComponent } from '../wizard';
import { NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep } from './wizard_steps/index';

@Component({
  templateUrl: './app/templates/configurations.html'
})
export class ConfigurationsComponent implements OnInit {
  model: PlaybookConfiguration = this.cleanModel();

  configurations: PlaybookConfiguration[] = null;
  playbooks: Playbook[] = [];
  servers: Server[] = [];
  shownConfigurationId: string = null;
  shownConfiguration: PlaybookConfiguration = null;
  configurationVersions: {[key: string]: PlaybookConfiguration[]} = {};
  @ViewChild(WizardComponent) wizard: WizardComponent;
  @ViewChild(Filter) filter: Filter;
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
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {
    this.fetchData();
    this.data.playbook().getAll()
      .then((playbooks: pagedResult) => {
        this.playbooks = playbooks.items;
      })
  }

  ngOnInit() {
    this.activatedRoute
      .fragment
      .subscribe((id: string) => {
        this.shownConfigurationId = id;
        if (id) {
          this.shownConfiguration = _.find(this.configurations, {id});
          if (!this.shownConfiguration) {
            this.data.configuration().find(id)
              .then(
                (configuration: PlaybookConfiguration) => {
                  this.shownConfiguration = configuration;
                },
                (error: any) => {
                  this.shownConfigurationId = null;
                  this.shownConfiguration = null;
                  return this.data.handleResponseError(error);
                }
              );
          }
        }
      });
  }

  getPlaybooksForFilter(): Object[] {
    return _.map(this.playbooks, (playbook: Playbook) => {
      return [playbook.name, playbook.id];
    });
  }

  fetchData(page: number = 1): Promise<any> {
    return this.data.configuration().findAll({
      filter: _.get(this.filter, 'query', {}),
      page
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
    if (model.id) {
      // Update configuration
      savePromise = this.data.configuration().postUpdate(model.id, model);
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
          this.modal.close();
          // Seems jsdata returns the payload as a part of create response.
          // Unneeded values should be removed.
          let pureConfig = new BaseModel(
            _.omit(configuration, ['playbook_id', 'cluster_id', 'name', 'server_ids', 'hints'])
          );
          this.model = pureConfig;
          this.refreshConfigurations(this.pagedData.page);
        }
      )
      .catch(
        (error: any) => this.data.handleResponseError(error)
      );
  }

  refreshConfigurations(page: number = 1) {
    if (this.shownConfigurationId) {
      this.getConfigurationVersions(this.shownConfigurationId, true);
    } else {
      this.fetchData(page);
    }
  }

  isCurrent(configuration: PlaybookConfiguration) {
    return this.shownConfigurationId === configuration.id;
  }

  getConfigurations() {
    return !this.shownConfigurationId
    ?
      (this.configurations ? this.configurations : [])
    :
      (!this.shownConfiguration ? [] : [this.shownConfiguration]);
  }

  getConfigurationVersions(configurationId: string, reread: boolean = false) {
    if (!this.configurationVersions[configurationId] || reread) {
      this.configurationVersions[configurationId] = [];
      this.data.configuration().getVersions(configurationId)
        .then(
          (versions: pagedResult) => {
            this.configurationVersions[configurationId] = versions.items;
          },
          (error: any) => this.data.handleResponseError(error)
        );
    }
    return this.configurationVersions[configurationId];
  }

  executeConfiguration(version: PlaybookConfiguration) {
    return this.data.execution().postCreate(
      new Record({playbook_configuration: {id: version.id, version: version.version}})
    ). then(
      () => this.router.navigate(['/executions']),
      (error: any) => this.data.handleResponseError(error)
    );
  }

  deleteConfiguration(configuration: PlaybookConfiguration) {
    if (!configuration.id) return;
    return this.data.configuration().destroy(configuration.id)
      .then(
        () => {
          this.shownConfigurationId = null;
          this.refreshConfigurations(this.pagedData.page);
        },
        (error: any) => this.data.handleResponseError(error)
      )
  }
}
