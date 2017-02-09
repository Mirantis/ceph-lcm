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
import { DataService, pagedResult } from '../../services/data';
import { Role } from '../../models';

// New user wizard step
@Component({
  templateUrl: './app/templates/wizard_steps/user.html'
})
export class UserStep extends WizardStepBase {
  private mandatoryFields = ['login', 'full_name', 'email'];
  private emailRegex = new RegExp('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{2,}\\.[a-zA-Z0-9-.]{2,}');
  roles: Role[] = [];

  init() {
    _.forEach(
      this.mandatoryFields,
      (property: string) => this.initModelProperty('data.' + property, '')
    );
    this.initModelProperty('data.role_id', null);
  }

  fetchData() {
    return this.data.role().findAll({})
      .then(
        (roles: pagedResult) => this.roles = roles.items,
        (error: any) => this.data.handleResponseError(error)
      );
  }

  isEmailValid() {
    return this.emailRegex.test(this.model.data.email);
  }

  isValid() {
    return !!_.get(this.model, 'data.role_id')
      && !_.some(this.mandatoryFields, (field: string) => !_.get(this.model.data, field))
      && this.isEmailValid();
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }
}
