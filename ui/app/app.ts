import { Component } from '@angular/core';
import { AuthService } from './services/auth';

@Component({
  selector: 'app',
  templateUrl: './app/templates/app.html'
})

export class AppComponent {
  constructor(private auth: AuthService) {
    auth.getLoggedUser();
  }

  getLoggedUserName(): string {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ?
      loggedUser.data.full_name + ' (' + loggedUser.data.login + ')' : '';
  }
}