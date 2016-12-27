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
  private configuration: PlaybookConfiguration;
  jsonConfiguration: string;

  init() {
    this.fetchData();
    this.initModelProperty('data.configuration', []);
    this.configuration = new PlaybookConfiguration({});
    this.jsonConfiguration = new JSONString().transform(
      _.get(this.model, 'data.configuration')
    );
  }

  constructor(wizard: WizardService, private data: DataService) {
    super(wizard);
  }

  fetchData() {
    if (!_.get(this.model, 'id')) {
      return;
    }
    return this.data.configuration().find(this.model.id)
      .then((configuration: PlaybookConfiguration) => {
        this.configuration = configuration;
      });
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

  isReadOnly() {
    return this.model.version !== this.configuration.version;
  }

}
