import * as _ from 'lodash';
import { Component } from '@angular/core';
import { WizardStepBase } from '../wizard_steps';
import { DataService, pagedResult } from '../../services/data';
import { WizardService } from '../../services/wizard';
import { Cluster } from '../../models';

// Configuration name and cluster selection
@Component({
  templateUrl: './app/templates/wizard_steps/name_and_cluster.html'
})
export class NameAndClusterStep extends WizardStepBase {
  clusters: Cluster[] = [];

  init() {
    this.initModelProperty('data.name', '');
    this.initModelProperty('data.cluster_id', '');
  }

  isValid() {
    return !!_.get(this.model, 'data.name') && !!_.get(this.model, 'data.cluster_id');
  }

  isShownInDeck() {
    return !_.get(this.model, 'id');
  }

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