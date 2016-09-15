import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';
import { Cluster } from '../models';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/clusters.html'
})
export class ClustersComponent {
  clusters: Cluster[] = null;
  newCluster: Cluster = new Cluster({});
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.cluster().findAll({})
      .then((clusters: Cluster[]) => this.clusters = clusters);
  }

  editCluster(cluster: Cluster = null) {
    this.newCluster = _.isNull(cluster) ? new Cluster({}) : cluster.clone();
    this.modal.show();
  }

  save() {
    this.error = null;
    var savePromise: Promise<any>;
    if (this.newCluster.id) {
      // Update cluster
      savePromise = this.data.cluster().update(this.newCluster.id, this.newCluster);
    } else {
      // Create new cluster
      savePromise = this.data.cluster().create(this.newCluster);
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