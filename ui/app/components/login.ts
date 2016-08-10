import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {AuthService} from '../services/auth';

@Component({
  template: `
<h3>Login Form</h3>
<div>
  User is currently logged {{auth.isLoggedIn() ? 'in' : 'out'}}
  <button (click)='login("a", "b")' *ngIf='!auth.isLoggedIn()'>Get In</button>
</div>
`
})

export class LoginComponent {
  constructor(public auth: AuthService, private router: Router) {}

  login(email: string, password: string) {
    return this.auth.login(email, password);
  };

  logout() {
    this.auth.logout()
      .catch(() => true);
  }
}
