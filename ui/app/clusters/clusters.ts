/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { Component, ViewChild, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Modal, Filter } from '../directives';
import { DataService, pagedResult } from '../services/data';
import { Cluster } from '../models';
import { WizardComponent } from '../wizard';
import { ClusterStep } from './wizard_steps/cluster';

import * as _ from 'lodash';
import * as $ from 'jquery';

@Component({
  templateUrl: './app/templates/clusters.html'
})
export class ClustersComponent implements OnInit {
  clusters: Cluster[] = null;
  model: Cluster = new Cluster({});
  @ViewChild(WizardComponent) wizard: WizardComponent;
  @ViewChild(Filter) filter: Filter;
  pagedData: pagedResult = {} as pagedResult;
  shownClusterId: string = null;
  shownCluster: Cluster = null;

  clusterSteps = [
    ClusterStep
  ];


  constructor(
    private data: DataService,
    private modal: Modal,
    private activatedRoute: ActivatedRoute
  ) {
    this.fetchData();
  }

  ngOnInit() {
    this.activatedRoute
      .fragment
      .subscribe((id: string) => {
        this.shownClusterId = id;
        if (id) {
          this.shownCluster = _.find(this.clusters, {id});
          if (!this.shownCluster) {
            this.data.cluster().find(id)
              .then(
                (cluster: Cluster) => {
                  this.shownCluster = cluster;
                },
                (error: any) => {
                  this.shownClusterId = null;
                  this.shownCluster = null;
                  return this.data.handleResponseError(error);
                }
              );
          }
        }
      });
  }

  isCurrent(cluster: Cluster) {
    return cluster && cluster.id === this.shownClusterId;
  }

  fetchData(page: number = 1) {
    return this.data.cluster().findAll({
      filter: _.get(this.filter, 'query', {}),
      page
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

  getClusters() {
    return !this.shownClusterId
    ?
      (this.clusters ? this.clusters : [])
    :
      (!this.shownCluster ? [] : [this.shownCluster]);
  }

  getKeyHalfsets(cluster: Cluster) {
    let keys = _.keys(cluster.data.configuration).sort();
    return _.chunk(keys, Math.ceil(keys.length / 2));
  }

  editCluster(cluster: Cluster = null) {
    this.model = cluster ? cluster.clone() : new Cluster({});
    this.wizard.init(this.model);
    this.modal.show();
  }

  save(model: Cluster) {
    var savePromise: Promise<any>;
    if (model.id) {
      // Update cluster
      savePromise = this.data.cluster().postUpdate(model.id, model);
    } else {
      // Create new cluster
      savePromise = this.data.cluster().postCreate(model);
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
