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
import { Component } from '@angular/core';
import { WizardStepBase } from '../../wizard_step';
import { DataService, pagedResult } from '../../services/data';
import { WizardService } from '../../services/wizard';
import { Server, Playbook, PlaybookConfiguration, PlaybookServersPolicies } from '../../models';

// Servers selection
@Component({
  templateUrl: './app/templates/wizard_steps/servers.html'
})
export class ServersStep extends WizardStepBase {
  servers: Server[] = [];

  init() {
    this.initModelProperty('data.server_ids', []);
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }

  getPolicyServers(): Server[] {
    let selectedPlaybook: Playbook = this.getSharedData('selectedPlaybook');
    if (!selectedPlaybook) {
      return this.servers;
    }

    let selectedClusterId = this.model.data.cluster_id;
    let differentiator = {
      'any_server':
        (server: Server) => true,
      'in_this_cluster':
        (server: Server) => server.data.cluster_id === selectedClusterId,
      'not_in_this_cluster':
        (server: Server) => server.data.cluster_id !== selectedClusterId,
      'in_other_cluster':
        (server: Server) => !!server.data.cluster_id && server.data.cluster_id !== selectedClusterId,
      'not_in_other_cluster':
        (server: Server) => !server.data.cluster_id || server.data.cluster_id === selectedClusterId,
      'in_any_cluster':
        (server: Server) => !!server.data.cluster_id,
      'not_in_any_cluster':
        (server: Server) => !server.data.cluster_id
    }[selectedPlaybook.server_list_policy];

    return _.filter(this.servers, differentiator);
  }

  fetchData() {
    return this.data.server().findAll({})
      .then((servers: pagedResult) => {
        this.servers = servers.items;
      });
  }

  isShownInDeck() {
    let selectedPlaybook: Playbook = this.getSharedData('selectedPlaybook');
    return !_.get(this.model, 'id') && _.get(selectedPlaybook, 'required_server_list', false);
  }

  isValid() {
    return !_.isEmpty(_.get(this.model, 'data.server_ids', []));
  }

  toggleServer(server: Server) {
    var server_ids = this.model.data.server_ids;
    this.model.data.server_ids = this.isServerSelected(server) ?
      _.without(server_ids, server.id) : server_ids.concat(server.id);
  }

  toggleSelectAll() {
    this.model.data.server_ids = this.areAllServersSelected()
    ?
      []
    :
      _.map(this.getPolicyServers(), 'id');
  }

  isServerSelected(server: Server) {
    return _.includes(this.model.data.server_ids, server.id);
  }

  areAllServersSelected() {
    return this.model.data.server_ids.length === this.getPolicyServers().length;
  }
}
