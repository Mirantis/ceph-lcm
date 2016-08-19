import {Component} from '@angular/core';
import {AuthService}   from '../services/auth';


@Component({
  templateUrl: './app/templates/login.html'
})
export class LoginComponent {
  constructor(public auth: AuthService) {}

  email: string;
  password: string;

  login() {
    return this.auth.login(this.email, this.password);
  };

  logout() {
    this.auth.logout()
      .catch(() => true);
  }
}
