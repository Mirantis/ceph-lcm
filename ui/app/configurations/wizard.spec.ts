import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';
import { Router } from '@angular/router';

import { WizardComponent } from './wizard';

import { AppModule } from '../app.module';
import { DataService, pagedResult } from '../services/data';
import { AuthService } from '../services/auth';
import { PlaybookConfiguration, Cluster } from '../models';
import * as _ from 'lodash';

import { MockDataService, createFakeData, amount, itemsPerPage } from '../../testing/mock.data';
import { MockAuthService } from '../../testing/mock.auth';
import { MockRouter } from '../../testing/mock.router';
import { DOMHelper } from '../../testing/dom';
import globals = require('../services/globals');

describe('Playbook (Plugin) Configuration wizard', () => {
  let fixture: ComponentFixture<WizardComponent>;
  let component: WizardComponent;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;

  beforeEach(
    done => {
      DataService
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService},
          {provide: Router, useClass: MockRouter}
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

  describe('step 1 (Playbook configuration)', () => {
    let clusterSelect: HTMLSelectElement;
    let nameInput: DOMHelper;
    let nextButton: HTMLButtonElement;

    beforeEach(() => {
      component.step = 1;
      fixture.detectChanges();
      clusterSelect = dom.select('select#configuration_cluster').element as HTMLSelectElement;
      nameInput = dom.select('input#configuration_name');
      nextButton = dom.select('.modal-footer button.btn-primary').element as HTMLButtonElement;
    });

    it('all clusters are available for selection', () => {
      component.clusters = createFakeData(10, Cluster).items;
      fixture.detectChanges();
      expect(clusterSelect.querySelectorAll('option').length).toEqual(10);
    });

    it('name is required to proceed', () => {
      component.newConfiguration.data.name = 'dummy configuration dummy name';
      fixture.detectChanges();
      expect(nextButton.disabled).toBeFalsy('Next button is enabled if name is entered');
      component.newConfiguration.data.name = '';
      fixture.detectChanges();
      expect(nextButton.disabled).toBeTruthy('Next button is disabled if no name entered');
    });
  });

});