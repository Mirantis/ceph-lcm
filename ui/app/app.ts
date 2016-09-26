import { Component } from '@angular/core';
import { AuthService } from './services/auth';
import { ErrorService } from './services/error';

@Component({
  selector: 'app',
  templateUrl: './app/templates/app.html'
})

export class AppComponent {
  errors: string[] = [];

  constructor(private auth: AuthService, private error: ErrorService) {
    auth.getLoggedUser();
    error.errorHappened.subscribe((error: any) => this.addError(error));
  }

  getLoggedUserName(): string {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ?
      loggedUser.data.full_name + ' (' + loggedUser.data.login + ')' : '';
  }

  addError(error: any) {
    if (this.auth.isLoggedIn()) {
      this.errors.push(error);
    }
  }

  dismissErrors() {
    this.errors = [];
  }
}