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