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
import { WizardService } from '../../services/wizard';

// Cluster name adjustment
@Component({
  templateUrl: './app/templates/wizard_steps/cluster.html'
})
export class ClusterStep extends WizardStepBase {
  init() {
    this.initModelProperty('data.name', '');
  }

  isValid() {
    return !!_.get(this.model, 'data.name');
  }

  constructor(wizard: WizardService) {
    super(wizard);
  }
}
