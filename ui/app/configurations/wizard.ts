import * as _ from 'lodash';
import { FormControl, FormGroup } from '@angular/forms';
import { Component, Input, Output, EventEmitter } from '@angular/core';

import { Modal } from '../directives';
import { DataService } from '../services/data';
import { ErrorService } from '../services/error';
import { Playbook, Cluster, Server, PlaybookConfiguration } from '../models';
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

  constructor(
    private data: DataService,
    private error: ErrorService,
    private modal: Modal
  ) {
  }

  validateServersStep() {
    if (this.step === 3) {
      // If switched to servers selection screen - make initial validation
      this.getValidationSummary();
    } else {
      // Otherwize clear errors from the previous steps
      this.error.clear();
    }
  }

  forward() {
    this.step += 1;
    this.validateServersStep();
  }

  backward() {
    this.step -= 1;
    this.validateServersStep();
  }

  getAllowedPlaybooks(): Playbook[] {
    if (!globals.loggedUserRole) {
      return [];
    }
    var playbooksPermissions = _.find(globals.loggedUserRole.data.permissions, {name: 'playbook'});
    return _.filter(
      this.playbooks,
      (playbook) => _.includes(playbooksPermissions.permissions, playbook.id)
    );
  }

  selectPlaybook(playbook: Playbook) {
    this.serversRequired = playbook.required_server_list;
    this.newConfiguration.data.playbook_id = playbook.id;
  }

  initForEditing(configuration: PlaybookConfiguration) {
    this.step = 4;
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
    return this.step >= 3 || (this.step === 2 && !this.serversRequired);
  }

  isSaveButtonDisabled(newConfigurationForm: FormGroup, editConfigurationForm: FormGroup) {
    return (this.step === 2 && !this.newConfiguration.data.playbook_id) ||
      (this.step === 3 && !this.areSomeServersSelected()) ||
      (this.step < 4 && !newConfigurationForm.valid) ||
      (this.step === 4 && !editConfigurationForm.valid) ||
      !this.isJSONValid();
  }

  toggleSelectAll() {
    this.newConfiguration.data.server_ids = this.areAllServersSelected() ?
      [] : _.map(this.servers, 'id') as string[];
    this.getValidationSummary();
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
          if (this.step !== 4) {
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