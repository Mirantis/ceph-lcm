import { Component } from '@angular/core';

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
    <li> <a [routerLink]="['/login']">Login</a>
    <li> <a [routerLink]="['/']">Home</a>
    <li> <a [routerLink]="['/dashboard']">Dashboard</a>

    <li class='right'> Logged as {{this.getLoggedUserName()}}
      <button (click)='auth.logout()'>Log out</button>
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