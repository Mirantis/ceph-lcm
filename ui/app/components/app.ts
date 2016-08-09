import {Component} from '@angular/core';
import {ROUTER_DIRECTIVES} from "@angular/router";
// import '../rxjs_operators';
import {AuthService} from '../services/auth';

@Component({
  selector: 'app',
  directives: [ROUTER_DIRECTIVES],
  template: `<ul *ngIf='auth.isLoggedIn()' class='navigation'>
      <li> <a routerLink='/login' routerLinkActive='active'>Login</a>
      <li> <a routerLink='/' routerLinkActive='active' [routerLinkActiveOptions]='{exact: true}'>Home</a>
      <li> <a routerLink='/dashboard' routerLinkActive='active'>Dashboard</a>
    </ul>

    <router-outlet></router-outlet>`
})

export class AppComponent {
  constructor(private auth: AuthService) {}
}
