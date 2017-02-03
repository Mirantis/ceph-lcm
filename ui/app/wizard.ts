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
import {
  Component, Input, Output, EventEmitter, ComponentRef, Injector,
  ViewChild, ViewChildren, ViewContainerRef, ComponentFactoryResolver, ComponentFactory
} from '@angular/core';

import { Modal } from './directives';
import { ErrorService } from './services/error';
import { WizardService } from './services/wizard';
import { BaseModel } from './models';
import { JSONString } from './pipes';
import globals = require('./services/globals');

@Component({
  selector: 'wizard',
  templateUrl: './app/templates/wizard.html'
})
export class WizardComponent {
  model: BaseModel = new BaseModel({data: {}});
  filledModel: BaseModel;
  isSingleStep = false;
  isReadOnly = false;
  @Input() steps: any[] = [];
  @Output() saveHandler = new EventEmitter();
  @ViewChild('step_container', {read: ViewContainerRef}) stepContainer: ViewContainerRef;

  step: number = 0;
  stepComponents: ComponentRef<any>[] = [];

  debug = false;
  jsonTransformer = new JSONString();
  stringified = '';

  constructor(
    private error: ErrorService,
    private modal: Modal,
    private resolver: ComponentFactoryResolver,
    private injector: Injector,
    private wizard: WizardService
  ) {
    wizard.model.subscribe((model: BaseModel) => {
      this.filledModel = model;
    });
  }

  public get currentStep(): ComponentRef<any> {
    return this.stepComponents[this.step];
  }

  getVisibleSteps() {
    let steps = _.filter(this.stepComponents, (component: any) => {
      return component.instance.isShownInDeck();
    });
    this.isSingleStep = steps.length === 1;
    return steps;
  }

  modelIsValid(): boolean {
    return !_.some(this.getVisibleSteps(), (step: any) => {
      return !step.instance.isValid();
    });
  }

  stepIsValid(): boolean {
    return this.currentStep.instance.isValid();
  }

  ngOnInit() {
    this.stepContainer.clear();
    this.stepComponents = _.map(this.steps, (component: any) => {
      let componentFactory: ComponentFactory<any> = this.resolver.resolveComponentFactory(component);
      let componentRef = componentFactory.create(this.injector);
      this.stepContainer.insert(componentRef.hostView);
      return componentRef;
    });
    this.init(new BaseModel({}));
  }

  ngDoCheck() {
    this.stringified = this.jsonTransformer.transform(_.get(this.filledModel, 'data', ''));
  }

  ngOnDestroy() {
    this.stepComponents.forEach((componentRef: ComponentRef<any>) => {
      componentRef.destroy();
    });
  }

  init(model: BaseModel, isReadOnly = false) {
    this.model = model;
    this.isReadOnly = isReadOnly;
    this.stepComponents.forEach((component: any, index: number) => {
      component.instance.model = this.model;
      component.instance.index = index;
      component.instance.isReadOnly = this.isReadOnly;
      component.instance.init();
    });
    let visibleSteps = this.getVisibleSteps();
    if (!visibleSteps.length) {
      return -1;
    }
    this.step = _.first(visibleSteps).instance.index;
    if (this.step >= 0) {
      this.go();
    }
  }

  renderStep() {
    this.wizard.currentStep.emit(this.currentStep);
  }

  getStep(offset: number): number {
    let visibleSteps = this.getVisibleSteps();
    let visibleIndex = _.findIndex(
      visibleSteps,
      (step, index) => step.instance.index === this.currentStep.instance.index
    );
    let nextIndex = offset + visibleIndex;
    if (visibleIndex < 0 || nextIndex < 0 || nextIndex >= visibleSteps.length) {
      return null;
    }
    return visibleSteps[nextIndex].instance.index;
  }

  go(offset: number = 0) {
    let nextIndex = this.getStep(offset);
    if (!_.isNull(nextIndex)) {
      this.step = nextIndex;
      this.renderStep();
    }
  }

  save() {
    this.saveHandler.emit(this.filledModel);
  }
}
