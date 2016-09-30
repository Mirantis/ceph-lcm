import * as _ from 'lodash';
import {Component} from '@angular/core';
import {AuthService}   from '../services/auth';
import {ErrorService}   from '../services/error';


@Component({
  templateUrl: './app/templates/login.html'
})
export class LoginComponent {
  username: string;
  password: string;
  loginError: {error: string, message: string} = null;

  constructor(public auth: AuthService, private error: ErrorService) {
    this.error.errorHappened.subscribe((error: any) => this.loginError = error);
  }

  getErrorMessage(): string {
    console.log(this.loginError);
    if (!this.loginError) {
      return '';
    }
    if (this.loginError.message.indexOf('Network') >= 0) {
      return this.loginError.message;
    }
    return `Authentication error. Please check that you've provided correct credentials.`;
  }

  login() {
    this.loginError = null;
    this.auth.login(this.username, this.password);
  }
}
