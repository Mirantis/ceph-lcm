import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {AuthService}   from '../services/auth';


@Component({
  template: `
<div class='login_form'>
  <div class='login' *ngIf='!auth.isLoggedIn()'>
  <form (ngSubmit)='login()' #loginForm='ngForm'>
    <h3>Login</h3>
    <input type='text' placeholder='E-mail' [(ngModel)]='email' name='email' required>
    <input type='password' placeholder='Password' [(ngModel)]='password' name='password' required>

    <button type='submit' [disabled]='!loginForm.form.valid'>Get In</button>
    </form>
  </div>
  <div *ngIf='auth.isLoggedIn()'>
    You're logged in already. Logout first to get back in as another user.
  </div>
</div>
`
})
export class LoginComponent {
  constructor(public auth: AuthService, private router: Router) {}

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
