import * as _ from 'lodash';
import { FormControl, FormGroup } from '@angular/forms';
import {
  Component, Input, Output, EventEmitter, ComponentRef, ReflectiveInjector, Injector,
  ViewChild, ViewChildren, ViewContainerRef, ComponentFactoryResolver, ComponentFactory
} from '@angular/core';

import { Modal } from '../directives';
import { ErrorService } from '../services/error';
import { WizardService } from '../services/wizard';
import { BaseModel, Playbook, Cluster, Server, PlaybookConfiguration, PermissionGroup, Hint } from '../models';
import { JSONString } from '../pipes';
import globals = require('../services/globals');

var formatJSON = require('format-json');

@Component({
  selector: 'wizard',
  templateUrl: './app/templates/wizard.html'
})
export class WizardComponent {
  @Input() model: BaseModel = new BaseModel({data: {}});
  @Input() steps: any[] = [];
  @Output() saveHandler = new EventEmitter();
  @ViewChild('step_container', {read: ViewContainerRef}) stepContainer: ViewContainerRef;

  step: number = 0;
  stepComponents: ComponentRef<any>[] = [];

  // jsonConfiguration: string;
  // serversRequired: boolean = false;
  // readonly: boolean = false;
  // selectedPlaybook: Playbook = null;

  constructor(
    private error: ErrorService,
    private modal: Modal,
    private resolver: ComponentFactoryResolver,
    private injector: Injector,
    private wizard: WizardService
  ) {
    wizard.model.subscribe((model: BaseModel) => {
      this.model = model;
    });
  }

  getConfigData() {
    return new JSONString().transform(_.get(this.model, 'data', ''));
  }

  getVisibleSteps() {
    return _.filter(this.stepComponents, (component: any) => {
      return component.instance.isShownInDeck();
    });
  }

  modelIsValid(): boolean {
    return !_.some(this.getVisibleSteps(), (step: any) => {
      return !step.instance.isValid();
    });
  }

  stepIsValid(): boolean {
    return this.stepComponents[this.step].instance.isValid();
  }

  ngAfterViewInit() {
    this.stepContainer.clear();
    this.steps.forEach((component: any) => {
      let componentFactory: ComponentFactory<any> = this.resolver.resolveComponentFactory(component);
      let componentRef = componentFactory.create(this.injector);
      this.stepContainer.insert(componentRef.hostView);
      this.stepComponents.push(componentRef);
    });
    this.init();
  }

  ngOnDestroy() {
    this.stepComponents.forEach((componentRef: ComponentRef<any>) => {
      componentRef.destroy();
    });
  }

  init(configuration: BaseModel = null) {
    this.stepComponents.forEach((component: any) => {
      component.instance.model = this.model;
    });
    this.step = _.indexOf(this.stepComponents, _.first(this.getVisibleSteps()));
    if (this.step >= 0) {
      this.go();
    }
  }

  renderStep() {
    this.wizard.currentStep.emit(this.stepComponents[this.step]);
  }

  getStep(offset: number): number {
    let visibleSteps = this.getVisibleSteps();
    let visibleIndex = _.indexOf(visibleSteps, this.stepComponents[this.step]);
    let nextIndex = offset + visibleIndex;
    if (visibleIndex < 0 || nextIndex < 0 || nextIndex >= visibleSteps.length) {
      return null;
    }
    return _.indexOf(visibleSteps, visibleSteps[nextIndex]);
  }

  go(offset: number = 0) {
    let nextIndex = this.getStep(offset);
    if (!_.isNull(nextIndex)) {
      this.step = nextIndex;
      this.renderStep();
    }
  }

  save() {
    this.saveHandler.emit(this.model);
  }










  // validateStep() {
  //   this.error.clear();
  //   switch (this.step) {
  //     case 3:
  //       // Playbook hints screen
  //       this.hintsValidity = {};
  //       break;
  //     case 4:
  //       // If switched to servers selection screen - make initial validation
  //       this.getValidationSummary();
  //       break;
  //   }
  // }

  // hintsAreValid() {
  //   return _.reduce(this.hintsValidity, (result: boolean, isValid: boolean) => {
  //     return result && isValid;
  //   }, true);
  // }





  // initForEditing(configuration: BaseModel) {
  //   this.step = 5;
  //   this.model = configuration;
  //   this.jsonConfiguration = formatJSON.plain(this.model.data.configuration);
  // }

  // isSaveButtonShown() {
  //   return this.step >= 4 || (
  //     this.step === 2 &&
  //     !this.serversRequired &&
  //     this.selectedPlaybook &&
  //     !this.selectedPlaybook.hints.length
  //   );
  // }

  // isSaveButtonDisabled(modelForm: FormGroup, editConfigurationForm: FormGroup) {
  //   return (this.step === 2 && !this.model.data.playbook_id) ||
  //     (this.step === 3 && !this.hintsAreValid()) ||
  //     (this.step === 4 && !this.areSomeServersSelected()) ||
  //     (this.step < 5 && !modelForm.valid) ||
  //     (this.step === 5 && !editConfigurationForm.valid) ||
  //     !this.isJSONValid();
  // }

  // toggleSelectAll() {
  //   this.model.data.server_ids = this.areAllServersSelected() ?
  //     [] : _.map(this.servers, 'id') as string[];
  //   this.getValidationSummary();
  // }

  // skipHints() {
  //   return !_.get(this.selectedPlaybook, 'hints.length', 0);
  // }


  // // TODO: Use Server type here
  // toggleServer(server: any) {
  //   var server_ids = this.model.data.server_ids;
  //   this.model.data.server_ids = this.isServerSelected(server) ?
  //     _.without(server_ids, server.id) : server_ids.concat(server.id);
  //   this.getValidationSummary();
  // }

  // isServerSelected(server: any) {
  //   return _.includes(this.model.data.server_ids, server.id);
  // }

  // areSomeServersSelected() {
  //   return this.model.data.server_ids.length;
  // }

  // areAllServersSelected() {
  //   return this.model.data.server_ids.length === this.servers.length;
  // }

  // isJSONValid() {
  //   if (_.isUndefined(this.jsonConfiguration)) {
  //     return true;
  //   }
  //   try {
  //     JSON.parse(this.jsonConfiguration);
  //   } catch (e) {
  //     return false;
  //   }
  //   return true;
  // }

  // getValidationSummary() {
  //   this.error.clear();
  //   if (!this.areSomeServersSelected()) {
  //     this.error.add('Validation Error', 'Servers selection is required');
  //   }
  // }

}