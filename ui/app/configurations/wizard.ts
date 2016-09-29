import * as _ from 'lodash';
import { FormControl } from '@angular/forms';
import { Component, Input, Output, EventEmitter } from '@angular/core';

import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { Playbook, Cluster, Server, PlaybookConfiguration } from '../models';

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

  newConfiguration: PlaybookConfiguration = new PlaybookConfiguration({data: {server_ids: []}});
  error: any = null;
  jsonConfiguration: string;
  serversRequired: boolean = false;

  constructor(private data: DataService, private modal: Modal) {
  }

  forward() {
    this.step += 1;
  }

  backward() {
    this.step -= 1;
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

  init(configuration: PlaybookConfiguration = null) {
    this.serversRequired = false;
    if (configuration) {
      this.initForEditing(configuration);
    } else {
      this.step = 1;
      this.newConfiguration = new PlaybookConfiguration({data: {server_ids: []}});
    }
  }

  isSaveButtonShown() {
    return this.step >= 3 || (this.step === 2 && !this.serversRequired);
  }

  toggleSelectAll() {
    this.newConfiguration.data.server_ids = this.areAllServersSelected() ?
      [] : _.map(this.servers, 'id') as string[];
  }

  // TODO: Use Server type here
  toggleServer(server: any) {
    var server_ids = this.newConfiguration.data.server_ids;
    this.newConfiguration.data.server_ids = this.isServerSelected(server) ?
      _.without(server_ids, server.id) : server_ids.concat(server.id);
  }

  isServerSelected(server: any) {
    return _.includes(this.newConfiguration.data.server_ids, server.id);
  }

  areSomeServersSelected() {
    return this.step !== 3 || this.newConfiguration.data.server_ids.length;
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

  getValidationSummary(): string {
    let summary: string[] = [];
    if (!this.areSomeServersSelected()) {
      summary.push('Servers selection is required.');
    }
    return summary.join('');
  }

  save() {
    this.error = null;
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
        (configuration: PlaybookConfiguration) => {
          this.callback.emit();
          if (this.step !== 4) {
            this.initForEditing(configuration);
          } else {
            this.modal.close();
          }
        }
      ).catch(
        (error: any) => this.data.handleResponseError(error)
      );
  }

}