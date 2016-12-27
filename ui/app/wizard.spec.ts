import { async, inject, TestBed, ComponentFixture, fakeAsync, tick } from '@angular/core/testing';
import { FormControl } from '@angular/forms';
import { APP_BASE_HREF } from '@angular/common';
import { Router } from '@angular/router';
import { Component, ComponentRef } from '@angular/core';

import { WizardComponent } from './wizard';
import { TestWizardStep } from './wizard_step';
import { WizardService } from './services/wizard'

import { AppModule } from './app.module';
import { DataService, pagedResult } from './services/data';
import { AuthService } from './services/auth';
import { PlaybookConfiguration, Cluster } from './models';
import * as _ from 'lodash';

import { MockDataService, createFakeData, amount, itemsPerPage } from '../testing/mock.data';
import { MockAuthService } from '../testing/mock.auth';
import { MockRouter } from '../testing/mock.router';
import { DOMHelper } from '../testing/dom';
import globals = require('./services/globals');
import { BaseModel } from './models';


describe('Wizard Component', () => {
  let fixture: ComponentFixture<WizardComponent>;
  let component: WizardComponent;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;
  let model: BaseModel = new BaseModel({});

  beforeEach(
    done => {
      DataService
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService}
        ]
      })
      .compileComponents()
      .then(done);
    }
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(WizardComponent);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
  });

  describe('with steps provided', () => {
    let step1: any;
    let step2: any;
    let instance1: any;
    let instance2: any;

    beforeEach(() => {
      component.steps = [TestWizardStep, TestWizardStep];
      component.ngOnInit();
      step1 = component.stepComponents[0];
      step2 = component.stepComponents[1];
      instance1 = step1.instance;
      instance2 = step2.instance;
      instance1.stepContainer.title = 'title1';
      instance2.stepContainer.title = 'title2';
    });

    it('initializes them with model', () => {
      let init = spyOn(instance1, 'init').and.callThrough();
      component.init(model);
      expect(init).toHaveBeenCalled();
      expect(instance1.model).toEqual(model);
    });

    it('makes sure step components are destroyed together with the wizard', () => {
      step1.destroy = jasmine.createSpy('destroy');
      step2.destroy = jasmine.createSpy('destroy');
      fixture.destroy();
      expect(step1.destroy).toHaveBeenCalled();
      expect(step2.destroy).toHaveBeenCalled();
    });

    it('shows only visible ones and detects single step cases', () => {
      expect(component.getVisibleSteps().length).toEqual(2);
      expect(component.isSingleStep).toBeFalsy();
      instance1.isShownInDeck = () => false;
      expect(component.getVisibleSteps().length).toEqual(1);
      expect(component.isSingleStep).toBeTruthy();
    })

    it('validates model based on each step validity', () => {
      expect(component.modelIsValid()).toBeTruthy();
      instance1.isValid = () => false;
      expect(component.modelIsValid()).toBeFalsy();
    });

    it('starts from the first visible step', () => {
      instance1.isShownInDeck = () => false;
      component.init(model);
      expect(component.step).toBe(1);
      expect(component.currentStep.instance.index).toBe(instance2.index);
    });

    it('synchronizes model back from steps to the wizard', done => {
      instance1.model.id = 'dummy_id';
      instance1.ngDoCheck();
      fixture.whenStable()
        .then(() => {
          expect(component.filledModel.id).toBe('dummy_id');
          done();
        });
    });

    it('allows switching between steps', done => {
      let go = spyOn(component, 'go').and.callThrough();
      let renderStep = spyOn(component, 'renderStep').and.callThrough();
      component.init(model);
      fixture.whenStable()
        .then(() => {
          expect(component.step).toEqual(0);
          expect(go).toHaveBeenCalled();
          expect(renderStep).toHaveBeenCalledTimes(1);

          expect(instance1.stepContainer.isSelected()).toBeTruthy();
          expect(instance2.stepContainer.isSelected()).toBeFalsy('aaa');
          expect(component.getStep(1)).toEqual(1);
          component.go(1);
          fixture.whenStable()
            .then(() => {
              expect(renderStep).toHaveBeenCalledTimes(2);
              expect(component.step).toEqual(1);
              expect(instance1.stepContainer.isSelected()).toBeFalsy();
              expect(instance2.stepContainer.isSelected()).toBeTruthy();
              done();
            });
        });
    });

    it('uses shared service to switch steps', () => {
      let wizardService = fixture.debugElement.injector.get(WizardService);
      let activateStep = spyOn(wizardService.currentStep, 'emit');
      component.renderStep();
      expect(activateStep).toHaveBeenCalledWith(step1);
    });

    it('allows shifting from current step by offset', () => {
      expect(component.step).toBe(0);
      expect(component.getStep(-1)).toBeNull('Unable to shift left');
      expect(component.getStep(1)).toBe(1);
      expect(component.getStep(2)).toBeNull('Right bound reached');
      instance2.isShownInDeck = () => false;
      expect(component.getStep(1)).toBeNull('Unable to move to hidden step');
    });

    it('allows switching between visible steps', () => {
      let renderStep = spyOn(component, 'renderStep');
      component.go(10);
      expect(renderStep).not.toHaveBeenCalled();
      component.go(1);
      expect(component.step).toBe(1);
      expect(renderStep).toHaveBeenCalled();
    });

    it('executes callback upon saving', () => {
      let wizardService = fixture.debugElement.injector.get(WizardService);
      component.saveHandler.subscribe((result: any) => {
        expect(result).toEqual(model);
      });
      wizardService.model.emit(model);
      component.save();
    });

    describe('renders UI properly', () => {
      let dom: any;

      beforeEach(() => {
        fixture.detectChanges();
        dom = new DOMHelper(fixture);
      });

      it('in edge cases (navigation buttons react to edges)', () => {
        expect(dom.select('#previous').isDisabled).toBeTruthy();
        expect(dom.select('#next').isDisabled).toBeFalsy();
        component.go(1);
        fixture.detectChanges();
        expect(dom.select('#previous').isDisabled).toBeFalsy();
        expect(dom.select('#next').isDisabled).toBeTruthy();
      });

      describe('based on steps validity', () => {
        beforeEach(() => {
          expect(component.modelIsValid()).toBeTruthy();
          component.currentStep.instance.isValid = () => false;
          fixture.detectChanges();
        });

        it('(Save button gets disabled)', () => {
          expect(dom.select('#save').isDisabled).toBeTruthy();
        });

        it('(Next button gets disabled)', () => {
          expect(dom.select('#next').isDisabled).toBeTruthy();
        });
      });

      describe('for readonly mode', () => {
        beforeEach(() => {
          component.isReadOnly = true;
          fixture.detectChanges();
        });

        it('(no Save button is shown)', () => {
          expect(dom.select('#save').isVisible).toBeFalsy();
        });

        it('(Discard button is named Close)', () => {
          expect(_.trim(dom.select('#close').innerText)).toBe('Close');
        });
      });

      describe('in case of single step', () => {
        beforeEach(() => {
          component.stepComponents[1].instance.isShownInDeck = () => false;
          component.getVisibleSteps();
          fixture.detectChanges();
        });

        it('(properly detected)', () => {
          expect(component.isSingleStep).toBeTruthy();
        });

        it('(Close button is rendered on the right if readonly)', () => {
          expect(dom.select('#close').className).toContain('pull-left');
          component.isReadOnly = true;
          fixture.detectChanges();
          expect(dom.select('#close').className).not.toContain('pull-left');
        });

        it('(Prev and Next buttons are not rendered)', () => {
          expect(dom.select('#previous').isVisible).toBeFalsy();
          expect(dom.select('#next').isVisible).toBeFalsy();
        });
      });
    });

  });

});