import { async, inject, TestBed, ComponentFixture } from '@angular/core/testing';
import { APP_BASE_HREF } from '@angular/common';

import { PasswordResetComponent } from './index';
import { AuthService } from '../../app/services/auth';

import { AppModule } from '../app.module';

describe('Password Reset Component', () => {
  let fixture: ComponentFixture<PasswordResetComponent>;
  let component: PasswordResetComponent;
  let mockAuth: any;
  let resetToken = 'token87853485';

  beforeEach(
    async(() => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          AuthService
        ]
      }).compileComponents()
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(PasswordResetComponent);
    component = fixture.componentInstance;
    mockAuth = fixture.debugElement.injector.get(AuthService);

    fixture.detectChanges();
  });

  it('renders reset form if no reset token provided', () => {
    expect(fixture.nativeElement.querySelector('form#reset')).not.toBeNull();
  });

  describe('when reset token is supplied', () => {
    it('and is not correct - reset form with an error message are shown', async(() => {
      mockAuth.checkPasswordResetToken = jasmine.createSpy('mockAuth').and.returnValue(Promise.reject('because'));
      component.checkProvidedToken(resetToken).then(() => {
        fixture.detectChanges();
        expect(mockAuth.checkPasswordResetToken).toHaveBeenCalledWith(resetToken);
        expect(component.resetToken).toBe(null);
        expect(fixture.nativeElement.querySelector('form#reset')).not.toBeNull();
      });
    }));

    describe('and is correct - ', () => {
      let prerequisites: any;
      let updateButton: any;
      let dummyPassword = 'dummy_password';

      beforeEach(() => {
        mockAuth.checkPasswordResetToken = jasmine.createSpy('mockAuth').and.returnValue(Promise.resolve());
        prerequisites = component.checkProvidedToken(resetToken).then(() => {
          fixture.detectChanges();
          updateButton = fixture.nativeElement.querySelector('button#update_password');
        });
      });

      it('password update form is rendered', async(() => {
        prerequisites.then(() => {
          expect(mockAuth.checkPasswordResetToken).toHaveBeenCalledWith(resetToken);
          expect(component.resetToken).toBe(resetToken);
          expect(fixture.nativeElement.querySelector('form#update')).not.toBeNull();
        });
      }));

      it('new password form should have proper validation', async(() => {
        prerequisites.then(() => {
          let assertSubmitIsDisabled = (state: boolean = true) => {
            fixture.detectChanges();
            expect(updateButton.disabled).toBe(state);
          };

          assertSubmitIsDisabled();

          component.password = dummyPassword;
          assertSubmitIsDisabled();

          component.passwordConfirmation = 'other_password';
          assertSubmitIsDisabled();

          component.passwordConfirmation = 'dummy_password';
          assertSubmitIsDisabled(false);
        });
      }));

      it('both token and new password should be passed to the backend as is', async(() => {
        mockAuth.updatePassword = jasmine.createSpy('mockAuth').and.returnValue(Promise.reject(''));
        prerequisites.then(() => {
          component.password = dummyPassword;
          component.passwordConfirmation = dummyPassword;
          fixture.detectChanges();
          updateButton.click();

          expect(mockAuth.updatePassword).toHaveBeenCalledWith(resetToken, dummyPassword);
        });
      }));
    });
  });
});