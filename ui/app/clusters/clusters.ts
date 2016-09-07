import { Component } from '@angular/core';
import { Modal } from '../bootstrap';
import { DataService } from '../services/data';

import * as _ from 'lodash';

@Component({
  templateUrl: './app/templates/clusters.html',
  directives: [Modal]
})
export class ClustersComponent {
  clusters: any[] = null;
  newCluster: any = {data: {}};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    this.data.cluster().findAll({})
      .then((clusters: any) => this.clusters = clusters.items);
  }

  editCluster(cluster: any = null) {
    this.newCluster = _.isNull(cluster) ? {data: {}} : cluster;
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