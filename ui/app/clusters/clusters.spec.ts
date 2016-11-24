import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { ClustersComponent } from './clusters';
import { AppModule } from '../app.module';
import { DataService, pagedResult } from '../services/data';
import { Cluster } from '../models';
import * as _ from 'lodash';

import { MockDataService, amount } from '../../testing/mock.data';
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
      DataService
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService}
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

  it('allows new clusters creation', () => {
    dom.click('.page-title .btn-primary')
      .then(() => {
        expect(dom.modal().isVisible).toBeTruthy();
        dom.click('.modal-footer .btn-primary');
        expect(dataService.cluster().postCreate).toHaveBeenCalledTimes(1);
      })
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

    it('displays received data in the tabular view', inject([DataService], (data: DataService) => {
      expect(component.clusters.length).toEqual(amount);
      expect(clustersTable).not.toBeNull();
      expect(noClustersDiv).toBeNull();
    }));

    it('displays exactly perPage records per page', inject([DataService], (data: DataService) => {
      let perPage = component.pagedData.per_page;
      let clusterRows = fixture.nativeElement.querySelectorAll('.clusters div.box');
      expect(perPage).toBeGreaterThan(0);
      expect(clusterRows.length).toEqual(perPage);
    }));

    it('makes request for data upon page switching', inject([DataService], (data: DataService) => {
      dom.select('ul.pagination li:nth-child(3) a')
        .then(function() {
          expect(this.innerText).toEqual('3');
        })
        .click();
      fixture.detectChanges();
      expect(dataService.cluster().findAll).toHaveBeenCalledWith(jasmine.objectContaining({page: 3}));
    }));

    it('allows cluster name editing', inject([DataService], (data: DataService) => {
      let dummyClusterName = 'new cluster name';

      dom.select('.clusters a .edit-icon').parent().click();
      expect(dom.modal().isVisible).toBeTruthy();
      fixture.detectChanges();
      component.newCluster.data.name = dummyClusterName;
      dom.click('.modal-footer .btn-primary');
      fixture.detectChanges();
      expect(dataService.cluster().postUpdate).toHaveBeenCalled();
    }));

    it('lets expand single cluster\'s configuration', () => {
      let expandCluster = (number?: number) => {
        if (number) {
          dom.select('.clusters .box:nth-child(' + number + ') a .glyphicon-triangle-right').parent();
        }
        dom.click();
        fixture.detectChanges();
      };
      expect(component.shownClusterId).toBeNull();
      expandCluster(3);
      expect(component.shownClusterId).toEqual('id1');
      expandCluster(6);
      expect(component.shownClusterId).toEqual('id4');
      expandCluster();
      expect(component.shownClusterId).toBeNull();
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