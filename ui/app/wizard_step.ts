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
import { Component, Input, EventEmitter, ViewChild, ComponentRef } from '@angular/core';
import { WizardService } from './services/wizard';
import { BaseModel } from './models';


// Transpiler component responsible for step visibility
// Every wizard step should be wrapped into the <step> tag
@Component({
  selector: 'step',
  template: `<div *ngIf="isSelected()" class="wizard-step"><h1>{{title}}</h1><ng-content></ng-content></div>`
})
export class WizardStepContainer {
  id = Math.random();
  @Input() title: string = '';
  private activeStep: ComponentRef<any>;

  isSelected(): boolean {
    return _.get(this.activeStep, 'instance.stepContainer.id', null) === this.id;
  }

  constructor(wizard: WizardService) {
    wizard.currentStep.subscribe((activeStep: ComponentRef<any>) => {
      this.activeStep = activeStep;
    });
  }
}

// Base wizard step class
export class WizardStepBase {
  @ViewChild(WizardStepContainer) stepContainer: WizardStepContainer;
  model: BaseModel;
  index = -1;
  isReadOnly = false;

  initModelProperty(key: string, defaultValue: any) {
    if (!_.get(this.model, key)) {
      _.set(this.model, key, defaultValue);
    }
  }

  init() {}

  getSharedData(key: string, defaultValue?: any): any {
    return _.get(this.wizard.sharedData, key, defaultValue);
  }

  setSharedData(key: string, value: any) {
    this.wizard.sharedData[key] = value;
    this.wizard.sharedDataUpdated.emit(key);
  }

  isShownInDeck(): boolean {
    return true;
  }

  isValid(): boolean {
    return true;
  }

  constructor(private wizard: WizardService) {
    this.init();
  }

  ngDoCheck() {
    this.wizard.model.emit(this.model);
  }
}

@Component({
  template: `<step><ng-content></ng-content></step>`
})
export class TestWizardStep extends WizardStepBase {
  constructor(wizard: WizardService) {
    super(wizard);
  }
}
