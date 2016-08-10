import {Component} from '@angular/core';
import {ROUTER_DIRECTIVES} from "@angular/router";
import {AuthService} from '../services/auth';
import * as _ from 'lodash';

@Component({
  selector: 'app',
  directives: [ROUTER_DIRECTIVES],
  template: `
<ul *ngIf='auth.isLoggedIn()' class='navigation'>
  <li> <a routerLink='/login' routerLinkActive='active'>Login</a>
  <li> <a routerLink='/' routerLinkActive='active' [routerLinkActiveOptions]='{exact: true}'>Home</a>
  <li> <a routerLink='/dashboard' routerLinkActive='active'>Dashboard</a>
  <li class='right'>
    Logged user: {{getLoggedUser()}}
    <button (click)='auth.logout()' *ngIf='auth.isLoggedIn()'>Log out</button>

</ul>

<router-outlet></router-outlet>
`
})

export class AppComponent {
  constructor(private auth: AuthService) {}

  getLoggedUser(): string {
    let user = this.auth.getLoggedUser();
    return user.data ? user.data.full_name + ' (' + user.data.login + ')' : '---';
  }
}
