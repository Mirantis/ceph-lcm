import * as _ from 'lodash';
import { FormControl, FormGroup } from '@angular/forms';
import { Component, Input, Output, EventEmitter } from '@angular/core';

import { Modal } from '../directives';
import { DataService } from '../services/data';
import { ErrorService } from '../services/error';
import { Playbook, Cluster, Server, PlaybookConfiguration, PermissionGroup, Hint } from '../models';
import globals = require('../services/globals');

var formatJSON = require('format-json');

@Component({
  selector: 'wizard',
  templateUrl: './app/templates/wizard.html'
})
export class WizardComponent {
  step: number = 1;
  @Input() playbooks: Playbook[];
  @Input() clusters: Cluster[];
  @Input() servers: Server[];
  @Output() callback = new EventEmitter();

  newConfiguration: PlaybookConfiguration = new PlaybookConfiguration({
    data: {
      server_ids: [],
      hints: []
    }
  });
  jsonConfiguration: string;
  serversRequired: boolean = false;
  readonly: boolean = false;
  selectedPlaybook: Playbook = null;
  hintsValidity: {[key: string]: boolean} = {};
  hints: {[key: string]: Hint} = {};

  constructor(
    private data: DataService,
    private error: ErrorService,
    private modal: Modal
  ) {
  }

  validateStep() {
    this.error.clear();
    switch (this.step) {
      case 3:
        // Playbook hints screen
        this.hintsValidity = {};
        break;
      case 4:
        // If switched to servers selection screen - make initial validation
        this.getValidationSummary();
        break;
    }
  }

  hintsAreValid() {
    return _.reduce(this.hintsValidity, (result: boolean, isValid: boolean) => {
      return result && isValid;
    }, true);
  }

  addHintValue(hint: Hint): Hint {
    let keptHint = this.hints[hint.id];
    hint.value = keptHint ? keptHint.value : hint.default_value;
    return hint;
  }

  forward(steps = 1) {
    this.step += steps;
    this.validateStep();
  }

  backward(steps = 1) {
    this.step -= steps;
    this.validateStep();
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
      this.playbooks,
      (playbook) => _.includes(playbooksPermissions.permissions, playbook.id)
    );
  }

  selectPlaybook(playbook: Playbook) {
    if (this.selectedPlaybook !== playbook) {
      this.hintsValidity = {};
      this.newConfiguration.data.hints = [] as [Hint];
      this.hints = {};
    }
    this.serversRequired = playbook.required_server_list;
    this.newConfiguration.data.playbook_id = playbook.id;
    this.selectedPlaybook = playbook;
  }

  initForEditing(configuration: PlaybookConfiguration) {
    this.step = 5;
    this.newConfiguration = configuration;
    this.jsonConfiguration = formatJSON.plain(this.newConfiguration.data.configuration);
  }

  init(configuration: PlaybookConfiguration = null, readonly = false) {
    this.serversRequired = false;
    this.readonly = readonly;
    if (configuration) {
      this.initForEditing(configuration);
    } else {
      this.step = 1;
      this.newConfiguration = new PlaybookConfiguration({
        data: {
          server_ids: [],
          hints: []
        }
      });
    }
  }

  isSaveButtonShown() {
    return this.step >= 4 || (
      this.step === 2 &&
      !this.serversRequired &&
      this.selectedPlaybook &&
      !this.selectedPlaybook.hints.length
    );
  }

  isSaveButtonDisabled(newConfigurationForm: FormGroup, editConfigurationForm: FormGroup) {
    return (this.step === 2 && !this.newConfiguration.data.playbook_id) ||
      (this.step === 3 && !this.hintsAreValid()) ||
      (this.step === 4 && !this.areSomeServersSelected()) ||
      (this.step < 5 && !newConfigurationForm.valid) ||
      (this.step === 5 && !editConfigurationForm.valid) ||
      !this.isJSONValid();
  }

  toggleSelectAll() {
    this.newConfiguration.data.server_ids = this.areAllServersSelected() ?
      [] : _.map(this.servers, 'id') as string[];
    this.getValidationSummary();
  }

  skipHints() {
    return !_.get(this.selectedPlaybook, 'hints.length', 0);
  }

  registerHint(data: {id: string, value: any, isValid: true}) {
    this.hints[data.id] = {id: data.id, value: data.value} as Hint;
    this.newConfiguration.data.hints = _.values(this.hints) as [Hint];
    this.hintsValidity[data.id] = data.isValid;
  }

  // TODO: Use Server type here
  toggleServer(server: any) {
    var server_ids = this.newConfiguration.data.server_ids;
    this.newConfiguration.data.server_ids = this.isServerSelected(server) ?
      _.without(server_ids, server.id) : server_ids.concat(server.id);
    this.getValidationSummary();
  }

  isServerSelected(server: any) {
    return _.includes(this.newConfiguration.data.server_ids, server.id);
  }

  areSomeServersSelected() {
    return this.newConfiguration.data.server_ids.length;
  }

  areAllServersSelected() {
    return this.newConfiguration.data.server_ids.length === this.servers.length;
  }

  isJSONValid() {
    if (_.isUndefined(this.jsonConfiguration)) {
      return true;
    }
    try {
      JSON.parse(this.jsonConfiguration);
    } catch (e) {
      return false;
    }
    return true;
  }

  getValidationSummary() {
    this.error.clear();
    if (!this.areSomeServersSelected()) {
      this.error.add('Validation Error', 'Servers selection is required');
    }
  }

  save() {
    this.error.clear();
    var savePromise: Promise<PlaybookConfiguration>;
    if (this.newConfiguration.id) {
      // Update configuration
      this.newConfiguration.data.configuration = JSON.parse(this.jsonConfiguration);
      savePromise = this.data.configuration().postUpdate(this.newConfiguration.id, this.newConfiguration);
    } else {
      // Create new configuration
      savePromise = this.data.configuration().postCreate(this.newConfiguration);
    }
    return savePromise
      .then(
        (configuration: Object) => {
          this.callback.emit();
          if (this.step !== 5) {
            // Seems jsdata returns the payload as a part of create response.
            // Unneeded values should be removed.
            let pureConfig = new PlaybookConfiguration(
              _.omit(configuration, ['playbook_id', 'cluster_id', 'name', 'server_ids'])
            );
            this.initForEditing(pureConfig);
          } else {
            this.modal.close();
          }
        }
      )
      .catch(
        (error: any) => this.data.handleResponseError(error)
      );
  }
}