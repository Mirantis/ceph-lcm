import { async, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { LoginComponent } from './index';
import { AuthService } from '../../app/services/auth';
import { AppModule } from '../app.module';

describe('Login Component', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let component: LoginComponent;

  beforeEach(
    async(() => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue : '/'},
          AuthService
        ]
      }).compileComponents()
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  describe('alert message', () => {
    let unauthorized = 'Unauthorized';
    let networkError = 'Network unreachable';
    let notFound = {error: '404', message: 'Not Found'};

    it('has proper css class assigned depending on type', () => {
      let assertAlertClass = (isError: boolean) => {
        let classes = component.getErrorClass();
        expect(classes['text-success']).toBe(!isError);
        expect(classes['text-danger']).toBe(isError);
      };

      component.loginError = {error: null, message: 'any'};
      assertAlertClass(false);

      component.loginError = notFound;
      assertAlertClass(true);

      component.resetErrors();
      expect(component.getErrorClass()).toEqual({});
    });

    it('gets reset properly', () => {
      component.loginError = notFound;
      component.resetErrors();
      expect(component.loginError).toBeNull();
    });

    it('is correctly printed', () => {
      component.resetErrors();
      expect(component.getErrorMessage()).toBe('');

      component.loginError = {error: 'any', message: networkError};
      expect(component.getErrorMessage()).toBe(networkError);

      component.loginError = {error: unauthorized, message: 'any'};
      expect(component.getErrorMessage()).toContain('Authentication error');

      component.loginError = notFound;
      expect(component.getErrorMessage()).toBe(notFound.message);
    });
  });

  describe('login form', () => {
    let submitButton: any;
    let authService: any;
    let login = 'dummy_login';
    let password = 'dummy_pass';

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