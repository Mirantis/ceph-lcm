import * as _ from 'lodash';
import { Component } from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { LoginComponent } from './login';
import { AuthService }   from '../services/auth';
import { ErrorService }   from '../services/error';

@Component({
  templateUrl: './app/templates/login.html'
})
export class PasswordResetComponent extends LoginComponent {
  resetToken: string = null;
  newPassword: string = null;

  constructor(
    public auth: AuthService,
    public error: ErrorService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    super(auth, error);
    this.reset = true;
  }

  ngOnInit() {
    this.route.params.forEach((params: Params) => {
      this.resetToken = params['reset_token'];
      if (this.resetToken) {
        this.auth.checkPasswordResetToken(this.resetToken)
          .then(
            () => {
              this.loginError = {error: '', message: 'Please enter the new password'}
            },
            (error: any) => {
              this.loginError = {error: 'Not Found', message: 'Password reset token was not found'};
              this.resetToken = null;
            }
          )
      }
    });
  }

  resetPassword() {
    this.resetErrors();
    this.auth.resetPassword(this.username)
      .then(
        (data: any) => {
          this.loginError = {error: '', message: 'Password reset instructions have been sent'};
        },
        (error: any) => {
          this.loginError = error.responseJSON;
        }
      )
  }

  updatePassword() {
    this.resetErrors();
    this.auth.updatePassword(this.resetToken, this.password)
      .then(
        (data: any) => {
          this.loginError = {error: '', message: 'Password reset instructions have been sent'};
        },
        (error: any) => {
          this.loginError = error.responseJSON;
        }
      )
  }
}
