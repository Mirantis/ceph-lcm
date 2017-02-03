import * as _ from 'lodash';
import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { JsonConfigurationStep } from './json_configuration';
import { AppModule } from '../../app.module';
import { BaseModel, Playbook, PlaybookConfiguration } from '../../models';
import { DataService, pagedResult } from '../../services/data';
import { MockDataService } from '../../../testing/mock.data';

import { DOMHelper } from '../../../testing/dom';
import globals = require('../../services/globals');

describe('Configuration wizard: json configuration step component', () => {
  let fixture: ComponentFixture<JsonConfigurationStep>;
  let component: JsonConfigurationStep;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;


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
    fixture = TestBed.createComponent(JsonConfigurationStep);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
    component.model = new BaseModel({});
    component.init();
  });

  it('initializes its own and model\'s properties', () => {
    component.init();
    expect(component.model.data.configuration).toEqual([]);
    expect(component.jsonConfiguration).toEqual('[]');
  });

  it('is shown in deck for existing configurations only (with ID)', () => {
    expect(component.isShownInDeck()).toBeFalsy();
    component.model.id = 'dummy id';
    expect(component.isShownInDeck()).toBeTruthy();
  });

  it('parses input into json', () => {
    expect(component.parseJSON('{"a": 1}')).toEqual({a: 1});
  });

  it('applies changes to the model if input is valid', () => {
    expect(component.model.data.configuration).toEqual([]);
    component.applyChanges('{');
    expect(component.model.data.configuration).toEqual([]);
    component.applyChanges('{"a": 2}');
    expect(component.model.data.configuration).toEqual({a: 2});
  });

  it('is valid if input is json-parsable', () => {
    component.jsonConfiguration = '{';
    expect(component.isValid()).toBeFalsy();
    component.jsonConfiguration = '{"a": 3}';
    expect(component.isValid()).toBeTruthy();
  });
});