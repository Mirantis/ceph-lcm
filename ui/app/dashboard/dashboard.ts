import {Component} from '@angular/core';
import { AuthService } from '../services/auth';
import { ErrorService } from '../services/error';

@Component({
  templateUrl: './app/templates/dashboard.html'
})
export class DashboardComponent {
  errors: string[] = [];

  constructor(private auth: AuthService, private error: ErrorService) {
    error.errorHappened.subscribe((error: any) => this.addError(error));
    auth.getLoggedUser();
  }

  getLoggedUserName(): string {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ? loggedUser.data.full_name : '';
  }

  addError(error: any) {
    this.errors.push(error);
  }

  dismissErrors() {
    this.errors = [];
  }

  logout() {
    this.auth.logout()
      .catch(() => true);
  }
}
