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
import { Cluster } from '../../models';

// Configuration name and cluster selection
@Component({
  templateUrl: './app/templates/wizard_steps/name_and_cluster.html'
})
export class NameAndClusterStep extends WizardStepBase {
  clusters: Cluster[] = [];

  init() {
    this.initModelProperty('data.name', '');
    this.initModelProperty('data.cluster_id', '');
  }

  isValid() {
    return !!_.get(this.model, 'data.name') && !!_.get(this.model, 'data.cluster_id');
  }

  isShownInDeck() {
    return !_.get(this.model, 'id');
  }

  fetchData() {
    return this.data.cluster().getAll()
      .then((clusters: pagedResult) => {
        this.clusters = clusters.items;
      });
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }
}
