import * as _ from 'lodash';
import { Component } from '@angular/core';
import { WizardStepBase } from '../wizard_steps';
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
