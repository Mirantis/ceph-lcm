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

import { UserStep } from './user';
import { AppModule } from '../../app.module';
import { BaseModel } from '../../models';
import { DataService, pagedResult } from '../../services/data';
import { AuthService } from '../../services/auth';
import { MockDataService } from '../../../testing/mock.data';
import { MockAuthService } from '../../../testing/mock.auth';

describe('New user wizard step', () => {
  let fixture: ComponentFixture<UserStep>;
  let component: UserStep;

  beforeEach(
    done => TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: DataService, useClass: MockDataService},
          {provide: AuthService, useClass: MockAuthService},
          {provide: APP_BASE_HREF, useValue: '/'}
        ]
      })
      .compileComponents()
      .then(done)
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(UserStep);
    component = fixture.componentInstance;
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model', () => {
    component.init();
    expect(component.model.data.login).toEqual('');
    expect(component.model.data.full_name).toEqual('');
    expect(component.model.data.email).toEqual('');
    expect(component.model.data.role_id).toBeNull();
  });

  it('fetches roles', done => {
    component.fetchData()
      .then(() => {
        let authService = fixture.debugElement.injector.get(AuthService);
        expect(authService.isAuthorizedTo).toHaveBeenCalledWith('view_role');

        let dataService = fixture.debugElement.injector.get(DataService);
        expect(dataService.role().getAll).toHaveBeenCalledTimes(2);

        done();
      })
  });

  it('is valid when its the fields are entered correctly', () => {
    expect(component.isValid()).toBeFalsy();
    component.model.data.login = 'Dummy Login';
    expect(component.isValid()).toBeFalsy();
    component.model.data.full_name = 'Dummy Name';
    expect(component.isValid()).toBeFalsy();
    component.model.data.role_id = '10';
    expect(component.isValid()).toBeFalsy();
    component.model.data.email = 'incorrect@email';
    expect(component.isValid()).toBeFalsy();
    component.model.data.email = 'correct@email.domain';
    expect(component.isValid()).toBeTruthy();
  });

});