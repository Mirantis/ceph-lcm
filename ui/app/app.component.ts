import { Component } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { AuthService } from './services/auth';

@Component({
  selector: 'app',
  template: `
<header>
  <h1>#cephilis</h1>
  <h2>Go get yours at Mirantis!</h2>
</header>

<navigation *ngIf='auth.isLoggedIn()'>
  <ul>
    <li> <a [routerLink]="['/dashboard']" routerLinkActive='active'>Dashboard</a>
    <li> <a [routerLink]="['/admin']" routerLinkActive='active'>Admin</a>

    <li class='right'> Logged as {{this.getLoggedUserName()}}
      <button (click)='auth.logout()' class='btn btn-sm'>Log out</button>
  </ul>
</navigation>

<router-outlet></router-outlet>
`
})

export class AppComponent {
  constructor(private auth: AuthService) {
    auth.getLoggedUser();
  }

  getLoggedUserName() {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ?
      loggedUser.data.full_name + ' (' + loggedUser.data.login + ')' : '';
  }
}