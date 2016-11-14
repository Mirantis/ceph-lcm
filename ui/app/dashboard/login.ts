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
