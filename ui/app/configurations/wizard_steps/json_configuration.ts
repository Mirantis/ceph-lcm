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
import { PlaybookConfiguration } from '../../models';
import { JSONString } from '../../pipes';

// Servers selection
@Component({
  templateUrl: './app/templates/wizard_steps/json_configuration.html'
})
export class JsonConfigurationStep extends WizardStepBase {
  jsonConfiguration: string;

  init() {
    this.initModelProperty('data.configuration', []);
    this.jsonConfiguration = new JSONString().transform(
      _.get(this.model, 'data.configuration')
    );
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
  }

  isShownInDeck() {
    return !!_.get(this.model, 'id', false);
  }

  parseJSON(value: string) {
    return JSON.parse(value);
  }

  applyChanges(value: string) {
    try {
      this.model.data.configuration = this.parseJSON(value);
    } catch (e) {
      // It's OK to have invalid JSON during the editing
    }
  }

  isValid() {
    try {
      this.parseJSON(this.jsonConfiguration);
    } catch (e) {
      return false;
    }
    return true;
  }
}
