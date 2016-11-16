import { DebugElement } from '@angular/core';
import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { APP_BASE_HREF } from '@angular/common';

import { LoginComponent } from './login';
import { AuthService } from '../../app/services/auth';
import { AppModule } from '../app.module';

describe('Login Component', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let component: LoginComponent;
  let login = 'dummy_login';
  let password = 'dummy_pass';
  let submitButton: any;
  let authService: any;

  beforeEach(
    async(() => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          AuthService,
          {provide: APP_BASE_HREF, useValue : '/'}
        ]
      }).compileComponents()
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });


  it('provides proper css class for the notification message', () => {
    let assertAlertClass = (isError: boolean) => {
      let classes = component.getErrorClass();
      expect(classes['text-success']).toBe(!isError);
      expect(classes['text-danger']).toBe(isError);
    };

    component.loginError = {error: null, message: 'message'};
    assertAlertClass(false);

    component.loginError = {error: '404', message: 'Not Found'};
    assertAlertClass(true);

    component.resetErrors();
    expect(component.getErrorClass()).toEqual({});
  });

  describe('login form', () => {
    beforeEach(() => {
      submitButton = fixture.nativeElement.querySelector('button[type=submit]');
    });

    it('requires both login & password to be entered to allow submission', () => {
      expect(submitButton.disabled).toBeTruthy();

      component.username = login;
      fixture.detectChanges();
      expect(submitButton.disabled).toBeTruthy();

      component.password = password;
      fixture.detectChanges();
      expect(submitButton.disabled).toBeFalsy();
    });

    it('passes provided credentials to the backend as is', () => {
        authService = fixture.debugElement.injector.get(AuthService);
        authService.login = jasmine.createSpy('login').and.returnValue(Promise.resolve({}));

        component.username = login;
        component.password = password;
        fixture.detectChanges();

        submitButton.click();
        expect(authService.login).toHaveBeenCalledWith(login, password);
      }
    );
  });
});