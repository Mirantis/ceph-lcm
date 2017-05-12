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

import * as _ from 'lodash';
import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { ServersStep } from './servers';
import { AppModule } from '../../app.module';
import { BaseModel, Playbook, Server } from '../../models';
import { DataService, pagedResult } from '../../services/data';
import { MockDataService } from '../../../testing/mock.data';

import { DOMHelper } from '../../../testing/dom';
import globals = require('../../services/globals');

describe('Configuration wizard: servers step component', () => {
  let fixture: ComponentFixture<ServersStep>;
  let component: ServersStep;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;
  let getServersIds = () => _.map(component.getPolicyServers(), 'id');

  beforeEach(
    done => TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: DataService, useClass: MockDataService},
          {provide: APP_BASE_HREF, useValue: '/'}
        ]
      })
      .compileComponents()
      .then(done)
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(ServersStep);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model properly', () => {
    expect(component.model.data.server_ids).toEqual([]);
  });

  it('fetches servers list from the backend', () => {
    let dataService = fixture.debugElement.injector.get(DataService);
    expect(dataService.server().getAll).toHaveBeenCalledTimes(1);
  });

  it('is only shown in deck for new configurations where servers are required', () => {
    component.model = new BaseModel({id: 'Dummy ID'});
    expect(component.isShownInDeck()).toBeFalsy();
    component.setSharedData('selectedPlaybook', new Playbook({required_server_list: true}));
    expect(component.isShownInDeck()).toBeFalsy();
    component.model = new BaseModel({});
    expect(component.isShownInDeck()).toBeTruthy();
  });

  it('is only valid if server[s] selected', () => {
    expect(component.isValid()).toBeFalsy();
    component.model.data.server_ids = ['dummy_id1', 'dummy_id2'];
    expect(component.isValid()).toBeTruthy();
  });

  describe('implements proper servers selection logic:', () => {
    let secondServer = new Server({id: 'dummy_id2'});
    let servers = [
      new Server({id: 'dummy_id1'}),
      secondServer,
      new Server({id: 'dummy_id3'})
    ];

    beforeEach(() => {
      component.servers = servers;
    });

    it('toggle server selection', () => {
      expect(component.model.data.server_ids).toEqual([]);
      component.toggleServer(secondServer);
      expect(component.model.data.server_ids).toEqual([secondServer.id]);
      component.toggleServer(secondServer);
      expect(component.model.data.server_ids).toEqual([]);
    });

    it('return server selection status', () => {
      expect(component.isServerSelected(secondServer)).toBeFalsy();
      component.toggleServer(secondServer);
      expect(component.isServerSelected(secondServer)).toBeTruthy();
    });

    it('all servers selection', () => {
      expect(component.model.data.server_ids).toEqual([]);
      component.toggleSelectAll();
      expect(component.model.data.server_ids).toEqual(getServersIds());
      component.toggleSelectAll();
      expect(component.model.data.server_ids).toEqual([]);
    });

    it('watch all selected state', () => {
      component.toggleServer(servers[0]);
      component.toggleServer(servers[2]);
      expect(component.areAllServersSelected()).toBeFalsy();
      component.toggleServer(secondServer);
      expect(component.areAllServersSelected()).toBeTruthy();
    })
  });

  describe('filters servers accordig to playbook\'s policy', () => {
    let imitatePolicy = (policy: string) => {
      return spyOn(component, 'getSharedData').and.returnValue(new Playbook({
        required_server_list: true,
        server_list_policy: policy
      }));
    };

    beforeEach(() => {
      component.model.data.cluster_id = 'dummy_cluster_id1';
      component.servers = _.map(_.range(0, 10), (index) => new Server({
        id: '' + index,
        data: {
          name: 'name' + index,
          fqdn: 'name' + index,
          ip: '10.10.0.' + index,
          cluster_id: index < 3 ? null : (index < 7 ? component.model.data.cluster_id : 'some_cluster_id')
        }
      }));
    });

    it('all servers are returned if no policy is provided', () => {
      imitatePolicy(null);
      expect(component.getPolicyServers().length).toBe(10);
    });

    it('returns all servers for "any_server" policy', () => {
      imitatePolicy('any_server');
      expect(component.getPolicyServers().length).toBe(10);
    });

    it('returns servers that belong to the selected cluster for "in_this_cluster" policy', () => {
      imitatePolicy('in_this_cluster');
      expect(getServersIds()).toEqual(['3', '4', '5', '6']);
    });

    it('returns servers that do not belong to the selected cluster for "not_in_this_cluster" policy', () => {
      imitatePolicy('not_in_this_cluster');
      expect(getServersIds()).toEqual(['0', '1', '2', '7', '8', '9']);
    });

    it('returns servers that are not in selected cluster for "in_other_cluster" policy', () => {
      imitatePolicy('in_other_cluster');
      expect(getServersIds()).toEqual(['7', '8', '9']);
    });

    it('returns unassigned servers or ones that belong to selected cluster for "not_in_other_cluster" policy', () => {
      imitatePolicy('not_in_other_cluster');
      expect(getServersIds()).toEqual(['0', '1', '2', '3', '4', '5', '6']);
    });

    it('returns assigned to clusters servers for "in_any_cluster" policy', () => {
      imitatePolicy('in_any_cluster');
      expect(getServersIds()).toEqual(['3', '4', '5', '6', '7', '8', '9']);
    });

    it('returns unassigned to clusters servers for "not_in_any_cluster" policy', () => {
      imitatePolicy('not_in_any_cluster');
      expect(getServersIds()).toEqual(['0', '1', '2']);
    });
  });
});
