import * as _ from 'lodash';
import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { APP_BASE_HREF } from '@angular/common';

import { HintComponent } from './hint';
import { AppModule } from '../app.module';
import { BaseModel, Hint } from '../models';
import { DOMHelper } from '../../testing/dom';


describe('Hint component', () => {
  let fixture: ComponentFixture<HintComponent>;
  let component: HintComponent;
  let mockData: any;
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
    fixture = TestBed.createComponent(HintComponent);
    component = fixture.componentInstance;
    dom = new DOMHelper(fixture);
  });

  function getDummyHint(addition: Object = {}): Hint {
    return _.assign({id: 'DummyID', description: 'Dummy description'}, addition) as Hint;
  };

  it('monitors model changes', () => {
    let onChange = spyOn(component, 'onChange');
    let newValue = 'dummy value';
    component.scheme = getDummyHint();
    expect(component.ngOnChanges({})).toBeUndefined();
    component.ngOnChanges({scheme: new SimpleChange(
      null, getDummyHint({value: newValue}), false
    )});
    fixture.detectChanges();
    expect(component.value).toBe(newValue);
    expect(onChange).toHaveBeenCalled();
  });

  describe('validates entered value according to hint type:', () => {
    let checkType = (
      type: string,
      incorrectValue: any,
      correctValue: any,
      inputType: string,
      additions: Object = {}
    ) => {
      component.scheme = getDummyHint(_.assign({type: type}, additions));
      if (!_.isNull(incorrectValue)) {
        component.value = incorrectValue;
        component.validate();
        expect(component.isValid).toBeFalsy();
      }
      component.value = correctValue;
      component.validate();
      expect(component.isValid).toBeTruthy();
      fixture.detectChanges();
      expect((dom.select('#DummyID').element as HTMLInputElement).type).toEqual(inputType);
    };

    it('integer', () => {
      checkType('integer', 'a', 123, 'number');
    });

    it('boolean', () => {
      checkType('boolean', null, true, 'checkbox');
    });

    it('string', () => {
      checkType('string', null, 'some text', 'text');
    });

    it('select', () => {
      checkType('select', 'incorrect', 'correct', 'select-one', {values: ['correct', 'correct2']});
    });
  });

  it('reports value changes back', done => {
    let validate = spyOn(component, 'validate');
    let result = 'dummy result';
    component.scheme = getDummyHint();
    component.callback.subscribe((value: any) => {
      expect(validate).toHaveBeenCalled();
      expect(value.value).toEqual(result);
      done();
    });
    component.result = result;
    component.onChange();
  });

  it('detects input controls for proper rendering', () => {
    component.scheme = getDummyHint({type: 'string'});
    expect(component.isInput()).toBeTruthy();
    component.scheme.type = 'boolean';
    expect(component.isInput()).toBeFalsy();
  });

});