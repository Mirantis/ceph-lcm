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
  @Input() title: string = '';  // Mandatory and unique for the single stepset
  private activeStep: ComponentRef<any>;

  isSelected(): boolean {
    return _.get(this.activeStep, 'instance.stepContainer.title', null) === this.title;
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
