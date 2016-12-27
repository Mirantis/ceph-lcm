import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { NameAndClusterStep } from './name_and_cluster';
import { AppModule } from '../../app.module';
import { DataService, pagedResult } from '../../services/data';
import { BaseModel } from '../../models';
import * as _ from 'lodash';

import { MockDataService, createFakeData, amount, itemsPerPage } from '../../../testing/mock.data';
import { DOMHelper } from '../../../testing/dom';

describe('Configuration wizard: name and cluster step component', () => {
  let fixture: ComponentFixture<NameAndClusterStep>;
  let component: NameAndClusterStep;
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
    fixture = TestBed.createComponent(NameAndClusterStep);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes model properties', () => {
    expect(component.model.data.name).toBe('');
    expect(component.model.data.cluster_id).toBe('');
  });

  it('is valid only when both values are entered', () => {
    expect(component.isValid()).toBeFalsy();
    component.model.data.name = 'Some name';
    expect(component.isValid()).toBeFalsy();
    component.model.data.cluster_id = 'Some ID';
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
    expect(dataService.cluster().findAll).toHaveBeenCalledWith({});
  });
});