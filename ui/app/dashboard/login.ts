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
import { AuthService }   from '../services/auth';
import { ErrorService }   from '../services/error';


@Component({
  templateUrl: './app/templates/login.html'
})
export class LoginComponent {
  username: string;
  password: string;
  loginError: {error: string, message: string} = null;
  reset = false;

  constructor(public auth: AuthService, public error: ErrorService) {
    this.error.errorHappened.subscribe((error: any) => this.loginError = error);
  }

  getErrorClass(): Object {
    if (!this.loginError) {
      return {};
    }
    return {
      'text-danger': !!this.loginError.error,
      'text-success': !this.loginError.error
    };
  }

  resetErrors() {
    this.loginError = null;
  }

  getErrorMessage(): string {
    if (!this.loginError) {
      return '';
    }
    if (this.loginError.message && this.loginError.message.indexOf('Network') >= 0) {
      return this.loginError.message;
    } else if (this.loginError.error === 'Unauthorized') {
      return `Authentication error. Please check that you've provided correct credentials.`;
    }
    return this.loginError.message;
  }

  login() {
    this.resetErrors();
    this.auth.login(this.username, this.password);
  }
}
