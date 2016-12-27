import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { PlaybookStep } from './playbook';
import { AppModule } from '../../app.module';
import { DataService, pagedResult } from '../../services/data';
import { BaseModel, Playbook, Role, PermissionGroup } from '../../models';
import * as _ from 'lodash';

import { MockDataService, createFakeData, amount, itemsPerPage } from '../../../testing/mock.data';
import { DOMHelper } from '../../../testing/dom';
import globals = require('../../services/globals');

describe('Configuration wizard: playbook step component', () => {
  let fixture: ComponentFixture<PlaybookStep>;
  let component: PlaybookStep;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;


  beforeEach(
    done => TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService},
        ]
      })
      .compileComponents()
      .then(done)
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(PlaybookStep);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model properties', () => {
    expect(component.selectedPlaybook).toBeNull();
    expect(component.model.data.playbook_id).toBe('');
  });

  it('is valid when playbook is chosen', () => {
    expect(component.isValid()).toBeFalsy();
    component.model.data.playbook_id = 'Some ID';
    expect(component.isValid()).toBeTruthy();
  });

  it('is shown in deck for new configurations only', () => {
    expect(component.isShownInDeck()).toBeTruthy();
    component.model = new BaseModel({id: 'Some ID'});
    expect(component.isShownInDeck()).toBeFalsy();
  });

  it('fetches clusters to bind the DDL', () => {
    let dataService = fixture.debugElement.injector.get(DataService);
    component.fetchData();
    expect(dataService.playbook().findAll).toHaveBeenCalledWith({});
  });

  it('shows only playbooks permitted by user\'s role', () => {
    let playbook2 = new Playbook({id: 'id2', name: 'name2'});
    component.playbooks = [
      new Playbook({id: 'id1', name: 'name1'}),
      playbook2,
      new Playbook({id: 'id3', name: 'name3'})
    ];
    globals.loggedUserRole = null;
    expect(component.getAllowedPlaybooks()).toEqual([]);
    globals.loggedUserRole = new Role({data: {
      permissions: [
        new PermissionGroup({
          name: 'playbook',
          permissions: [
            playbook2.id
          ]
        })
      ]
    }});
    expect(component.getAllowedPlaybooks()).toEqual([playbook2]);
  });

  describe('upon playbook selection', () => {
    let dummyPlaybook = new Playbook({
      id: 'dummy_id',
      hints: 'whatever_hints'
    });

    it('fills model properly', () => {
      component.selectPlaybook(dummyPlaybook);
      expect(component.model.data.playbook_id).toBe(dummyPlaybook.id);
      expect(component.model.data.hints).toBe(dummyPlaybook.hints);
      expect(component.model.data.server_ids).toEqual([]);
    });

    it('does not reset selected servers for the same playbook', () => {
      component.model.data.server_ids = ['server_id1', 'server_id2'];
      component.selectPlaybook(dummyPlaybook);
      expect(component.model.data.server_ids).toEqual([]);
      component.model.data.server_ids = ['server_id3'];
      component.selectPlaybook(dummyPlaybook);
      expect(component.model.data.server_ids).toEqual(['server_id3']);
    });
  });
});