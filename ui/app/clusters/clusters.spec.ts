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

import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { ClustersComponent } from './clusters';
import { AppModule } from '../app.module';
import { ActivatedRoute } from '@angular/router';
import { DataService, pagedResult } from '../services/data';
import { AuthService } from '../services/auth';
import { Cluster } from '../models';
import * as _ from 'lodash';

import { MockDataService, amount } from '../../testing/mock.data';
import { MockAuthService } from '../../testing/mock.auth';
import { MockActivatedRoute } from '../../testing/mock.router';
import { DOMHelper } from '../../testing/dom';

describe('Clusters Component', () => {
  let fixture: ComponentFixture<ClustersComponent>;
  let component: ClustersComponent;
  let mockData: any;
  let clustersTable: any;
  let noClustersDiv: any;
  let dataService: any;
  let dom: DOMHelper;

  beforeEach(
    done => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService},
          {provide: AuthService, useClass: MockAuthService},
          {provide: ActivatedRoute, useClass: MockActivatedRoute}
        ]
      })
      .compileComponents()
      .then(done);
    }
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(ClustersComponent);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
  });

  it('allows new clusters creation', done => {
    dom.click('.page-title .btn-primary')
      .then(() => {
        expect(dom.modal().isVisible).toBeTruthy();
        expect(dom.select('#save').isDisabled).toBeTruthy('Save disabled if no name entered');
        dom.select('#cluster_name').setValue('Dummy name')
          .then(() => {
            dom.click('#save');
            expect(dataService.cluster().postCreate).toHaveBeenCalledTimes(1);
            done();
          });
      });
  });

  describe('with existing clusters', () => {
    beforeEach(done => {
      return component.fetchData()
        .then(() => {
          fixture.detectChanges();
          clustersTable = fixture.nativeElement.querySelector('div.clusters');
          noClustersDiv = fixture.nativeElement.querySelector('div.no-clusters');
          done();
        });
    });

    it('displays received data in the tabular view', done => {
      let perPage = component.pagedData.per_page;
      expect(component.clusters.length).toEqual(perPage);
      expect(clustersTable).not.toBeNull();
      expect(noClustersDiv).toBeNull();
      done();
    });

    it('displays exactly perPage records per page', done => {
      let perPage = component.pagedData.per_page;
      let clusterRows = fixture.nativeElement.querySelectorAll('.clusters div.box');
      expect(perPage).toBeGreaterThan(0);
      expect(clusterRows.length).toEqual(perPage);
      done();
    });

    it('makes request for data upon page switching', done => {
      dom.select('ul.pagination li:nth-child(3) a')
        .then(function() {
          expect(this.innerText).toEqual('3');
        })
        .click();
      expect(dataService.cluster().findAll).toHaveBeenCalledWith(jasmine.objectContaining({page: 3}));
      done();
    });

    it('allows cluster name editing', done => {
      let dummyClusterName = 'new cluster name';

      dom.select('.clusters a .edit-icon').parent().click();
      expect(dom.modal().isVisible).toBeTruthy();
      fixture.detectChanges();
      component.model.data.name = dummyClusterName;
      dom.click('.modal-footer .btn-primary');
      expect(dataService.cluster().postUpdate).toHaveBeenCalled();
      done();
    });
  });

  describe('for for single cluster configuration', () => {
    let [server1, server2, server3] = [{server_id: 1}, {server_id: 2}, {server_id: 3}];
    let dummyCluster = new Cluster({
      data: {
        configuration: {
          zxy_role: [server1],
          afh_role: [server1, server2],
          role1: [server2, server3],
          anotherRole: []
        }
      }
    });

    it('calculates size in servers properly', () => {
      expect(component.getSize(dummyCluster)).toEqual(3);
    });

    it('displays keys sorted and in two columns', () => {
      expect(component.getKeyHalfsets(dummyCluster)).toEqual([
        ['afh_role', 'anotherRole'], ['role1', 'zxy_role']
      ]);
    });
  });

});
