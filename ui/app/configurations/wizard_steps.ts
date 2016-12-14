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


@Component({
  selector: 'step',
  template: `<div *ngIf="isSelected()"><h1>{{title}}</h1><ng-content></ng-content></div>`
})
export class WizardStepContainer {
  @Input() title: string = '';
  isVisible = false;
  activeStep: ComponentRef<any>;
  isSelected(): boolean {
    return this.activeStep && this.activeStep.instance && this.activeStep.instance.stepContainer === this;
  }
  constructor(wizard: WizardService) {
    wizard.currentStep.subscribe((activeStep: ComponentRef<any>) => {
      this.activeStep = activeStep;
    });
  }
};


export class WizardStepBase {
  @ViewChild(WizardStepContainer) stepContainer: WizardStepContainer;
  model: BaseModel;

  public getSharedData(key: string, defaultValue?: any): any {
    return _.get(this.wizard.sharedData, key, defaultValue);
  }
  public setSharedData(key: string, value: any) {
    this.wizard.sharedData[key] = value;
    this.wizard.sharedDataUpdated.emit(key);
  }

  isShownInDeck(): boolean {
    return true;
  }

  isValid(): boolean {
    return true;
  }

  constructor(private wizard: WizardService) {}

  ngDoCheck() {
    this.wizard.model.emit(this.model);
  }
}

@Component({
  templateUrl: './app/templates/wizard_steps/name_and_cluster.html'
})
export class NameAndClusterStep extends WizardStepBase {
  clusters: Cluster[] = [];

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
      console.log(this.model.data.hints.length, playbook.hints.length);
    }
  }
}

@Component({
  templateUrl: './app/templates/wizard_steps/hints.html'
})
export class HintsStep extends WizardStepBase {
  hintsValidity: {[key: string]: boolean} = {};
  hints: {[key: string]: Hint} = {};
  selectedPlaybook: Playbook;

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
    wizard.sharedDataUpdated.subscribe((key: string) => {
      if (key === 'selectedPlaybook') {
        this.selectedPlaybook = this.getSharedData('selectedPlaybook');
        this.hints = {};
        this.hintsValidity = {};
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
