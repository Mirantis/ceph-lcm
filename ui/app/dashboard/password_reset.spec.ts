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

import { PasswordResetComponent } from './index';
import { AuthService } from '../../app/services/auth';

import { AppModule } from '../app.module';
import { DOMHelper } from '../../testing/dom';

describe('Password Reset Component', () => {
  let fixture: ComponentFixture<PasswordResetComponent>;
  let component: PasswordResetComponent;
  let mockAuth: any;
  let resetToken = 'token87853485';
  let dom: DOMHelper;

  beforeEach(
    done => {
      return TestBed.configureTestingModule({
        imports: [AppModule],
        providers: [
          {provide: APP_BASE_HREF, useValue: '/'},
          AuthService
        ]
      })
      .compileComponents()
      .then(done);
    }
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(PasswordResetComponent);
    component = fixture.componentInstance;
    mockAuth = fixture.debugElement.injector.get(AuthService);
    dom = new DOMHelper(fixture);

    fixture.detectChanges();
  });

  it('renders reset form if no reset token provided', () => {
    expect(dom.select('form#reset').isVisible).toBeTruthy();
  });

  describe('when reset token is supplied', () => {
    it('and is not correct - reset form with an error message are shown', done => {
      mockAuth.checkPasswordResetToken = jasmine.createSpy('mockAuth').and.returnValue(Promise.reject('because'));
      component.checkProvidedToken(resetToken).then(() => {
        fixture.detectChanges();
        expect(mockAuth.checkPasswordResetToken).toHaveBeenCalledWith(resetToken);
        expect(component.resetToken).toBe(null);
        expect(dom.select('form#reset').isVisible).toBeTruthy();
        done();
      });
    });

    describe('and is correct -', () => {
      let prerequisites: any;
      let updateButton: any;
      let dummyPassword = 'dummy_password';

      beforeEach(() => {
        mockAuth.checkPasswordResetToken = jasmine.createSpy('mockAuth').and.returnValue(Promise.resolve());
        prerequisites = component.checkProvidedToken(resetToken).then(() => {
          fixture.detectChanges();
          updateButton = dom.select('button#update_password').element;
        });
      });

      it('password update form is rendered', done => {
        prerequisites.then(() => {
          expect(mockAuth.checkPasswordResetToken).toHaveBeenCalledWith(resetToken);
          expect(component.resetToken).toBe(resetToken);
          expect(dom.select('form#update').isVisible).toBeTruthy();
          done();
        });
      });

      it('new password form should have proper validation', done => {
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
          done();
        });
      });

      it('both token and new password should be passed to the backend as is', done => {
        mockAuth.updatePassword = jasmine.createSpy('mockAuth').and.returnValue(Promise.reject(''));

        prerequisites.then(() => {
          component.password = dummyPassword;
          component.passwordConfirmation = dummyPassword;
          fixture.detectChanges();
          updateButton.click();

          expect(mockAuth.updatePassword).toHaveBeenCalledWith(resetToken, dummyPassword);
          done();
        });
      });
    });
  });
});
