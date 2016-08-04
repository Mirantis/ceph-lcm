import {Component} from '@angular/core';
import {Router} from '@angular/router';

import {AuthService} from '../services/auth';

@Component({
  selector: 'login',
  template: `<h2>Login Form</h2>
  <div>User is currently logged {{authService.isLoggedIn() ? 'in' : 'out'}}</div>
<button (click)='login("a", "b")'>Get In</button>
<button (click)='logout()'>Log out</button>
  `
})

export class LoginComponent {
  constructor(public authService: AuthService, private router: Router) {}

  login(email: string, password: string) {
    this.authService.login(email, password).subscribe((result) => {
      if (result) {
        this.router.navigate(['dashboard']);
      }
    });
  };

  logout() {
    this.authService.logout();    
  }
}
