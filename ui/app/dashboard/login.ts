import {Component} from '@angular/core';
import {AuthService}   from '../services/auth';


@Component({
  template: `
<div class='login_form'>
  <div class='login' *ngIf='!auth.isLoggedIn()'>
  <form (ngSubmit)='login()' #loginForm='ngForm'>
    <h3>Login</h3>
    <input type='text' placeholder='E-mail' [(ngModel)]='email' name='email' class='form-control' required>
    <input type='password' placeholder='Password' [(ngModel)]='password' name='password' class='form-control' required>

    <button type='submit' [disabled]='!loginForm.form.valid' class='btn'>Get In</button>
    </form>
  </div>
  <div *ngIf='auth.isLoggedIn()'>
    You're logged in already. Logout first to get back in as another user.
  </div>
</div>
`
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
