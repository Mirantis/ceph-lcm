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

import { RoleApiPermissionsStep } from './role_permissions_group';
import { AppModule } from '../../app.module';
import { BaseModel } from '../../models';
import { DataService, pagedResult } from '../../services/data';
import { Role, PermissionGroup } from '../../models';
import { MockDataService } from '../../../testing/mock.data';

describe('Role wizard: permissions group step', () => {
  let fixture: ComponentFixture<RoleApiPermissionsStep>;
  let component: RoleApiPermissionsStep;
  let dataService: MockDataService;
  let targetGroup = new PermissionGroup({name: 'api', permissions: ['permission1', 'permission2']});

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
    fixture = TestBed.createComponent(RoleApiPermissionsStep);
    component = fixture.componentInstance;
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model', () => {
    component.init();
    expect(component.model.data.permissions).toEqual([]);
  });

  it('fetches its data and picks corresponding permissions group', done => {
    let dataService = fixture.debugElement.injector.get(DataService);
    dataService.permission().findAll = jasmine.createSpy('findAll')
      .and.returnValue(
        Promise.resolve({items: [
            new PermissionGroup({name: 'a', permissions: []}),
            targetGroup,
            new PermissionGroup({name: 'b', permissions: []})
          ]} as pagedResult)
        );

    component.fetchData()
      .then(() => {
        expect(dataService.permission().findAll).toHaveBeenCalledWith({});
        expect(component.allGroupPermissions).toEqual(targetGroup);
        done();
      });
  });

  describe('uses model\'s permissions group', () => {
    beforeEach(() => {
      component.model = new Role({});
      component.init();
      expect(component.modelGroupPermissions).toEqual([]);
      component.model = new Role({
        name: 'Dummy Role',
        data: {
          permissions: [
            new PermissionGroup({name: 'a', permissions: ['permission_a']}),
            targetGroup,
            new PermissionGroup({name: 'c', permissions: ['permission_c', 'permission_d']})
          ]
        }
      });
    });

    it('that corresponds to given group name', () => {
      expect(component.modelGroupPermissions).toEqual(targetGroup.permissions);
    });

    it('to get their states', () => {
      expect(component.getGroupPermission('permission1')).toBeTruthy();
      expect(component.getGroupPermission('not_found')).toBeFalsy();
    });

    it('to toggle separate ones\' states', () => {
      component.toggleGroupPermission('permission1');
      expect(component.getGroupPermission('permission1')).toBeFalsy();
      component.toggleGroupPermission('not_found');
      expect(component.getGroupPermission('not_found')).toBeTruthy();
    });
  });

});