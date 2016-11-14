import { DebugElement } from '@angular/core';
import { async, TestBed, ComponentFixture } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { APP_BASE_HREF } from '@angular/common';

import { LoginComponent } from './login';
import { AppModule } from '../app.module';

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let component: LoginComponent;

  beforeEach(
    async(() => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [{provide: APP_BASE_HREF, useValue : '/'}]
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

  it('checks that login form is rendered and allows logging in', () => {
    // let login: DebugElement = fixture.debugElement.query(By.css('input[name=username]'));
    // let password: DebugElement = fixture.debugElement.query(By.css('input[name=password]'));

    // login.nativeElement.value = 'root';
    // password.nativeElement.value = 'root';

  });
});