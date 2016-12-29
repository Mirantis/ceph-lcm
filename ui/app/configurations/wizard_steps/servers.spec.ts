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
    component.fetchData();
    expect(dataService.server().findAll).toHaveBeenCalledWith({});
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
      component.allServerIds = _.map(servers, 'id') as string[];
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
      expect(component.model.data.server_ids).toEqual(component.allServerIds);
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
});