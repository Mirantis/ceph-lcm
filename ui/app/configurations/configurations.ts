import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/configurations.html',
  directives: [Modal]
})
export class ConfigurationsComponent {
  configurations: any[] = [];
  newConfiguration: any = {data: {}};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.configuration().findAll({})
      .then((configurations: any) => this.configurations = configurations.items);
  }

  editConfiguration(configuration: any = null) {
    this.newConfiguration = _.isNull(configuration) ? {data: {}} : configuration;
    this.modal.show();
  }

  save() {
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
          this.modal.close();
          this.fetchData();
        },
        (error) => {this.error = error}
      );
  }
}