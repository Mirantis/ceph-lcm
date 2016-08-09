import {Component} from '@angular/core';
import {Router} from '@angular/router';

import {SessionService} from '../services/session';
import {AuthService} from '../services/auth';

@Component({
  template: `<h2>Login Form</h2>
  <div>User is currently logged {{auth.isLoggedIn() ? 'in' : 'out'}}</div>
<button (click)='login("a", "b")' *ngIf='!auth.isLoggedIn()'>Get In</button>
<button (click)='logout()' *ngIf='auth.isLoggedIn()'>Log out</button>
  `
})

export class LoginComponent {
  constructor(public auth: AuthService, public session: SessionService, private router: Router) {}

  login(email: string, password: string) {
    return this.session.login(email, password)
      .then((url: string) => {
        if (url) {
          this.router.navigate([url || 'dashboard']);
        }
      },
      (error: any) => {
        console.warn(error);
        return true;
      });
  };

  logout() {
    this.session.logout()
      .catch(() => true);
  }
}
