import {Component} from '@angular/core';
import {AuthService}   from '../services/auth';
import {ErrorService}   from '../services/error';


@Component({
  templateUrl: './app/templates/login.html'
})
export class LoginComponent {
  username: string;
  password: string;
  loginError: any = null;

  constructor(public auth: AuthService, private error: ErrorService) {
    this.error.errorHappened.subscribe((error: any) => this.loginError = error);
  }

  login() {
    this.loginError = null;
    this.auth.login(this.username, this.password);
  }
}
