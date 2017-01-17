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
import { DataService } from '../../services/data';
import { WizardService } from '../../services/wizard';
import { Hint, Playbook } from '../../models';

// Playbook configuration (hints) - omitted if playbook has no hints
@Component({
  templateUrl: './app/templates/wizard_steps/hints.html'
})
export class HintsStep extends WizardStepBase {
  hintsValidity: {[key: string]: boolean} = {};
  hints: {[key: string]: Hint} = {};
  selectedPlaybook: Playbook;

  init() {
    this.hints = {};
    this.hintsValidity = {};
    this.selectedPlaybook = null;
    this.initModelProperty('data.hints', []);
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    wizard.sharedDataUpdated.subscribe((key: string) => {
      if (key === 'selectedPlaybook') {
        this.init();
        this.selectedPlaybook = this.getSharedData('selectedPlaybook');
      }
    });
  }

  isShownInDeck() {
    return !_.get(this.model, 'id') && _.get(this.selectedPlaybook, 'hints', []).length > 0;
  }

  isValid() {
    return !_.some(this.hintsValidity, (isValid: boolean) => !isValid);
  }

  addHintValue(hint: Hint): Hint {
    let keptHint = this.hints[hint.id];
    hint.value = keptHint ? keptHint.value : hint.default_value;
    return hint;
  }

  registerHint(data: {id: string, value: any, isValid: true}) {
    this.hints[data.id] = {id: data.id, value: data.value} as Hint;
    this.model.data.hints = _.values(this.hints) as [Hint];
    this.hintsValidity[data.id] = data.isValid;
  }
}
