import { Component, ViewChild } from '@angular/core';
import { Modal, Filter, Pager } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { Cluster } from '../models';

import * as _ from 'lodash';
import * as $ from 'jquery';

@Component({
  templateUrl: './app/templates/clusters.html'
})
export class ClustersComponent {
  clusters: Cluster[] = null;
  newCluster: Cluster = new Cluster({});
  @ViewChild(Filter) filter: Filter;
  @ViewChild(Pager) pager: Pager;
  pagedData: pagedResult = {} as pagedResult;
  shownClusterId: string = null;

  constructor(private data: DataService, private modal: Modal) {
    this.fetchData();
  }

  fetchData() {
    return this.data.cluster().findAll({
      filter: _.get(this.filter, 'query', {}),
      page: _.get(this.pager, 'page', 1)
    })
      .then(
        (clusters: pagedResult) => {
          this.clusters = clusters.items;
          this.pagedData = clusters;
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }

  getSize(cluster: Cluster): number {
    let allRoles = _.concat([], ..._.values(cluster.data.configuration) as Object[][]);
    return _.uniq(_.map(allRoles, 'server_id')).length;
  }

  getKeyHalfsets(cluster: Cluster) {
    let keys = _.keys(cluster.data.configuration).sort();
    return _.chunk(keys, Math.ceil(keys.length / 2));
  }

  showConfig(cluster: Cluster) {
    this.shownClusterId = this.shownClusterId === cluster.id ?
      null : cluster.id;
  }

  editCluster(cluster: Cluster = null) {
    this.newCluster = _.isNull(cluster) ? new Cluster({}) : cluster.clone();
    this.modal.show();
  }

  save() {
    var savePromise: Promise<any>;
    if (this.newCluster.id) {
      // Update cluster
      savePromise = this.data.cluster().postUpdate(this.newCluster.id, this.newCluster);
    } else {
      // Create new cluster
      savePromise = this.data.cluster().postCreate(this.newCluster);
    }
    return savePromise
      .then(
        () => {
          this.modal.close();
          this.fetchData();
        },
        (error: any) => this.data.handleResponseError(error)
      );
  }
}