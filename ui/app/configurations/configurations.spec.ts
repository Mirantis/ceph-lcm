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

import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';

import { ConfigurationsComponent } from './configurations';
import { AppModule } from '../app.module';
import { DataService, pagedResult } from '../services/data';
import { AuthService } from '../services/auth';
import { PlaybookConfiguration } from '../models';
import * as _ from 'lodash';

import { MockDataService, createFakeData, amount, itemsPerPage } from '../../testing/mock.data';
import { MockAuthService } from '../../testing/mock.auth';
import { MockRouter, MockActivatedRoute } from '../../testing/mock.router';
import { DOMHelper } from '../../testing/dom';

describe('Playbook (Plugin) Configuration Component', () => {
  let fixture: ComponentFixture<ConfigurationsComponent>;
  let component: ConfigurationsComponent;
  let mockData: any;
  let dataService: MockDataService;
  let dom: DOMHelper;

  beforeEach(
    done => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          {provide: DataService, useClass: MockDataService},
          {provide: ActivatedRoute, useClass: MockActivatedRoute}
        ]
      })
      .compileComponents()
      .then(done);
    }
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationsComponent);
    component = fixture.componentInstance;
    dataService = TestBed.get(DataService);
    dom = new DOMHelper(fixture);
  });

  it('fetches its data', done => {
    component.fetchData()
      .then(() => {
        expect(dataService.configuration().findAll).toHaveBeenCalled();
        expect(component.configurations.length).toEqual(itemsPerPage);
        expect(component.pagedData.per_page).toEqual(itemsPerPage);
        expect(dataService.playbook().getAll).toHaveBeenCalled();
        expect(component.playbooks.length).toEqual(amount);
        done();
      });
  });

  it('prepares playbooks list for filtering', done => {
    component.fetchData()
      .then(() => {
        expect(component.playbooks.length).toEqual(amount);
        let playbooks = component.getPlaybooksForFilter();
        expect(playbooks.length).toEqual(amount);
        expect(_.head(playbooks)).toEqual(['Dummy Name 0', 'id0']);
        done();
      });
  });

  it('allows new configuration creation', () => {
    spyOn(component, 'editConfiguration').and.callThrough();
    dom.click('.page-title .btn-primary');
    expect(component.editConfiguration).toHaveBeenCalledTimes(1);
    expect(dataService.cluster().getAll).toHaveBeenCalledTimes(1);
    expect(dataService.playbook().getAll).toHaveBeenCalledTimes(2);
    expect(dataService.server().getAll).toHaveBeenCalledTimes(1);
    expect(dom.modal().isVisible).toBeTruthy();
  });

  describe('for single configuration expanded', () => {
    let getVersions: jasmine.Spy;
    let configuration: PlaybookConfiguration;
    let areVersionsVisible = () => {
      return dom.select('.configurations .box .bowels').isVisible;
    }

    beforeEach(done => {
      getVersions = spyOn(component, 'getConfigurationVersions').and.callThrough();
      component.fetchData()
        .then(() => {
          configuration = component.configurations[0];
          component.shownConfiguration = configuration;
          component.shownConfigurationId = configuration.id;
          fixture.detectChanges();
          fixture.whenStable().then(done);
        });
    });

    it('its versions are shown', () => {
      expect(areVersionsVisible()).toBeTruthy();
    });

    it('second click makes it collapsed', done => {
      expect(component.isCurrent(configuration)).toBeTruthy();
      expect(areVersionsVisible()).toBeTruthy();

      component.shownConfigurationId = null;
      fixture.detectChanges();

      fixture.whenStable()
        .then(() => {
          expect(component.isCurrent(configuration)).toBeFalsy();
          expect(areVersionsVisible()).toBeFalsy();
          done();
        });
    });

    it('versions are fetched', () => {
      expect(component.getConfigurationVersions).toHaveBeenCalledWith('id0');
      expect(dataService.configuration().getVersions).toHaveBeenCalled();
    });

    it('versions fetched are cached', () => {
      expect(dataService.configuration().getVersions).toHaveBeenCalledTimes(1);
      component.getConfigurationVersions(configuration.id);
      expect(dataService.configuration().getVersions).toHaveBeenCalledTimes(1);
    });

    it('user can execute it', () => {
      spyOn(component, 'executeConfiguration').and.callThrough();

      component.configurationVersions[configuration.id] =
        createFakeData(10, PlaybookConfiguration).items;

      fixture.detectChanges();
      dom.click('.box.open button.btn-success');
      expect(component.executeConfiguration).toHaveBeenCalledWith(configuration);
      expect(dataService.execution().postCreate).toHaveBeenCalled();
    });

    it('its deletion refreshes the view', done => {
      let refresh = spyOn(component, 'refreshConfigurations');
      dataService.configuration().destroy.and.returnValue(Promise.resolve());

      component.deleteConfiguration(configuration)
        .then(() => {
          expect(component.shownConfigurationId).toBeNull();
          expect(refresh).toHaveBeenCalledTimes(1);
          done();
        });
    });
  });

});
