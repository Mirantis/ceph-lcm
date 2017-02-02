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

import { RoleNameStep } from './role_name';
import { AppModule } from '../../app.module';
import { BaseModel } from '../../models';

describe('Role wizard: name step', () => {
  let fixture: ComponentFixture<RoleNameStep>;
  let component: RoleNameStep;

  beforeEach(
    done => TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'}
        ]
      })
      .compileComponents()
      .then(done)
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(RoleNameStep);
    component = fixture.componentInstance;
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model', () => {
    component.init();
    expect(component.model.data.name).toEqual('');
  });

  it('is valid when the name is entered', () => {
    expect(component.isValid()).toBeFalsy();
    component.model.data.name = 'Dummy Name';
    expect(component.isValid()).toBeTruthy();
  });

});