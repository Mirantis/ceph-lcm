import { Component, Input, Output } from '@angular/core';
import { DataService } from '../services/data';

import { Modal } from '../bootstrap';

import * as _ from 'lodash';

@Component({
  selector: 'wizard',
  templateUrl: './app/templates/wizard.html',
  directives: [Modal]
})
export class WizardComponent {
  step: number = 1;
  @Input() playbooks: Object[];
  @Input() clusters: Object[];
  @Input() servers: Object[];
  @Input() fetchData: Function;

  newConfiguration: any = {server_ids: []};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
  }

  forward() {
    this.step += 1;
  }

  backward() {
    this.step -= 1;
  }

  isSaveButtonShown() {
    var areServersInvolved = _.get(
      this.newConfiguration, 'playbook.required_server_list', false
    );
    return this.step === 3 || (this.step === 2 && !areServersInvolved);
  }

  toggleSelectAll() {
    this.newConfiguration.server_ids = this.areAllServersSelected() ?
      [] : _.map(this.servers, 'id');
  }

  areAllServersSelected() {
    return this.newConfiguration.server_ids.length === this.servers.length;
  }

  toggleServer(server: any) {
    var server_ids = this.newConfiguration.server_ids;
    this.newConfiguration.server_ids = this.isServerSelected(server) ?
      _.without(server_ids, server.id) : server_ids.concat(server.id);
  }

  isServerSelected(server: any) {
    return _.includes(this.newConfiguration.server_ids, server.id);
  }

  areSomeServersSelected() {
    return this.step !== 3 || this.newConfiguration.server_ids.length;
  }

  save() {
    this.newConfiguration.playbook = this.newConfiguration.playbook.id;
    this.error = null;
    var savePromise: Promise<any>;
    if (this.newConfiguration.id) {
      // Update configuration
      savePromise = this.data.configuration().update(this.newConfiguration.id, this.newConfiguration);
    } else {
      // Create new configuration
      savePromise = this.data.configuration().create(this.newConfiguration);
    }
    return savePromise
      .then(
        () => {
          this.fetchData();
          this.modal.close();
        },
        (error) => {this.error = error}
      );
  }

}