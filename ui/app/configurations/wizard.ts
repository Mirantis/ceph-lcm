import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormControl } from '@angular/forms';

import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { Playbook, Cluster, Server, PlaybookConfiguration } from '../models';

import * as _ from 'lodash';

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

  constructor(private data: DataService, private modal: Modal) {
  }

  forward() {
    this.step += 1;
  }

  backward() {
    this.step -= 1;
  }

  init(configuration: PlaybookConfiguration = null) {
    if (configuration) {
      this.step = 4;
      this.newConfiguration = configuration;
      this.jsonConfiguration = JSON.stringify(this.newConfiguration.data.configuration);
    } else {
      this.step = 1;
      this.newConfiguration = new PlaybookConfiguration({data: {server_ids: []}});
    }
  }

  isSaveButtonShown() {
    var areServersInvolved = _.get(
      this.newConfiguration, 'playbook.required_server_list', false
    );
    return this.step >= 3 || (this.step === 2 && !areServersInvolved);
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
    if (!this.isJSONValid()) {
      summary.push('Configuration should be in valid JSON format.');
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
          if (this.step === 3) {
            this.newConfiguration = configuration;
            this.forward();
          } else {
            this.modal.close();
          }
        }
      ).catch(
        (error: any) => this.data.handleResponseError(error)
      );
  }

}