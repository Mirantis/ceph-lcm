import * as _ from 'lodash';
import { FormControl, FormGroup } from '@angular/forms';
import { Component, Directive, Input, Output, EventEmitter, ViewContainerRef,
  ViewChild, Inject, forwardRef, Injectable, Host, ComponentRef, SimpleChanges } from '@angular/core';

import { Modal } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { ErrorService } from '../services/error';
import { WizardService } from '../services/wizard';
import { BaseModel, Playbook, Cluster, Server, PlaybookConfiguration, PermissionGroup, Hint } from '../models';
import globals = require('../services/globals');

var formatJSON = require('format-json');

// Transpiler component responsible for step visibility
// Every wizard step should be wrapped into the <step> tag
@Component({
  selector: 'step',
  template: `<div *ngIf="isSelected()"><h1>{{title}}</h1><ng-content></ng-content></div>`
})
export class WizardStepContainer {
  @Input() title: string = '';
  private activeStep: ComponentRef<any>;

  isSelected(): boolean {
    // console.log(222, this.activeStep.componentType.name);
    return _.get(this.activeStep, 'instance.stepContainer.title') === this.title;
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
  };

  fetchData() {
    return this.data.cluster().findAll({})
      .then((clusters: pagedResult) => {
        this.clusters = clusters.items;
      });
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }
}


// Playbook selection
@Component({
  templateUrl: './app/templates/wizard_steps/playbook.html'
})
export class PlaybookStep extends WizardStepBase {
  playbooks: Playbook[] = [];

  public get selectedPlaybook(): Playbook {
    return this.getSharedData('selectedPlaybook');
  }
  public set selectedPlaybook(playbook: Playbook) {
    this.setSharedData('selectedPlaybook', playbook);
  }

  init() {
    this.selectedPlaybook = null;
    this.initModelProperty('data.playbook_id', '');
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    this.fetchData();
  }

  fetchData() {
    return this.data.playbook().findAll({})
      .then((playbooks: pagedResult) => this.playbooks = playbooks.items);
  }

  isShownInDeck() {
    return true;
  }

  isValid() {
    return !!_.get(this.model, 'data.playbook_id');
  }

  getAllowedPlaybooks(): Playbook[] {
    if (!globals.loggedUserRole) {
      return [];
    }
    var playbooksPermissions = _.find(
      globals.loggedUserRole.data.permissions,
      {name: 'playbook'}
    ) || new PermissionGroup();
    return _.filter(
      this.playbooks, (playbook) => _.includes(playbooksPermissions.permissions, playbook.id)
    );
  }

  selectPlaybook(playbook: Playbook) {
    if (!this.selectedPlaybook || this.selectedPlaybook.id !== playbook.id) {
      this.selectedPlaybook = playbook;
      this.model.data.hints = playbook.hints;
      this.model.data.playbook_id = playbook.id;
    }
  }
}


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
    return _.get(this.selectedPlaybook, 'hints', []).length > 0;
  }

  isValid() {
    return !_.some(this.hintsValidity, false);
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


// Playbook selection
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

  fetchData() {
    return this.data.server().findAll({})
      .then((servers: pagedResult) => this.servers = servers.items);
  }

  isShownInDeck() {
    let selectedPlaybook: Playbook = this.getSharedData('selectedPlaybook');
    return _.get(selectedPlaybook, 'required_server_list', false);
  }

  isValid() {
    return !_.isEmpty(_.get(this.model, 'data.server_ids', []));
  }

  areAllServersSelected() {
    return this.model.data.server_ids.length === this.servers.length;
  }

}

