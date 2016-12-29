import * as _ from 'lodash';
import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { ClusterStep } from './cluster';
import { AppModule } from '../../app.module';
import { BaseModel } from '../../models';

import globals = require('../../services/globals');

describe('Configuration wizard: json configuration step component', () => {
  let fixture: ComponentFixture<ClusterStep>;
  let component: ClusterStep;
  let mockData: any;


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
    fixture = TestBed.createComponent(ClusterStep);
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