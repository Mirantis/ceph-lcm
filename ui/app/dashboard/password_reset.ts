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

import * as _ from 'lodash';
import { Component } from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { LoginComponent } from './login';
import { AuthService }   from '../services/auth';
import { ErrorService }   from '../services/error';

@Component({
  templateUrl: './app/templates/login.html'
})
export class PasswordResetComponent extends LoginComponent {
  resetToken: string = null;
  passwordConfirmation: string = null;

  constructor(
    public auth: AuthService,
    public error: ErrorService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    super(auth, error);
    this.reset = true;
  }

  ngOnInit() {
    this.route.params.forEach((params: Params) => {
      let token = params['reset_token'];
      if (token) {
        this.checkProvidedToken(token);
      }
    });
  }

  checkProvidedToken(token: string) {
    return this.auth.checkPasswordResetToken(token)
      .then(
        () => {
          this.loginError = {error: '', message: 'Please enter the new password'};
          this.resetToken = token;
        },
        (error: any) => {
          this.loginError = {error: 'Not Found', message: 'Password reset token was not found'};
          this.resetToken = null;
        }
      );
  }

  resetPassword() {
    this.resetErrors();
    this.auth.resetPassword(this.username)
      .then(
        (data: any) => {
          this.loginError = {error: '', message: 'Password reset instructions have been sent'};
        },
        (error: any) => {
          this.loginError = error.responseJSON;
        }
      )
  }

  updatePassword() {
    this.resetErrors();
    this.auth.updatePassword(this.resetToken, this.password)
      .then(
        (data: any) => {
          this.loginError = {error: '', message: 'Password has been saved'};
          this.router.navigate(['/login']);
        },
        (error: any) => {
          this.loginError = error.responseJSON;
        }
      )
  }
}
