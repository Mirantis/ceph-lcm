import {Component} from '@angular/core';
import {Router} from '@angular/router';

import {AuthService} from '../services/auth';

@Component({
  selector: 'login',
  template: `<div>Login Form</div>
<button (click)='onSubmit("a", "b")'>Get In</button>
  `
})

export class LoginComponent {
  constructor(public authService: AuthService, private router: Router) {}

  onSubmit(email: string, password: string) {
    console.log('Submitted')
    this.authService.login(email, password).subscribe((result) => {
      if (result) {
        this.router.navigate(['dashboard']);
      }
    });
  }
}
