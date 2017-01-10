import * as _ from 'lodash';
import { inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { DashboardComponent } from './dashboard';
import { AppModule } from '../app.module';
import { ErrorService } from '../services/error';
import { AuthService } from '../services/auth';
import { Modal } from '../directives';

import { User } from '../models';

import { DOMHelper } from '../../testing/dom';

describe('Dashboard component', () => {
  let fixture: ComponentFixture<DashboardComponent>;
  let component: DashboardComponent;
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
    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    dom = new DOMHelper(fixture);
  });

  it('subscribes to emitted error messages', () => {
    let errorService: ErrorService = fixture.debugElement.injector.get(ErrorService);
    let addErrorSpy = spyOn(component, 'addError');
    let error = 'Dummy Error';

    errorService.errorHappened.emit(error);
    expect(addErrorSpy).toHaveBeenCalledWith(error);
  });

  it('displays logged user\'s name', () => {
    let authService: AuthService = fixture.debugElement.injector.get(AuthService);
    authService.loggedUser = null;

    expect(component.getLoggedUserName()).toEqual('');
    authService.loggedUser = {data: {full_name: 'Dummy Name'}} as User;
    expect(component.getLoggedUserName()).not.toEqual('');
  });

  it('displays errors only if no modal is open', () => {
    let modal: Modal = fixture.debugElement.injector.get(Modal);
    let isOpenedSpy = spyOn(modal, 'isOpened').and.returnValue(true);
    let error = 'Dummy Error';

    expect(component.errors.length).toBe(0);
    component.addError(error);
    expect(component.errors.length).toBe(0);

    isOpenedSpy.and.returnValue(false);
    component.addError(error);
    expect(component.errors.length).toBe(1);
  });

  it('dismisses error messages', () => {
    component.errors = ['1', 'a', 'true'];
    component.dismissErrors();
    expect(component.errors.length).toBe(0);
  });

});