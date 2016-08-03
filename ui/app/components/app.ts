import {Component} from '@angular/core';
import {ROUTER_DIRECTIVES} from "@angular/router";

@Component({
  selector: 'vsm-app',
  directives: [ROUTER_DIRECTIVES],
  template: `    <ul class='navigation'>
      <li> <a routerLink='/login'>Login</a>
      <li> <a routerLink='/'>Home</a>
      <li> <a routerLink='/dashboard'>Dashboard</a>
    </ul>

    <router-outlet></router-outlet>`
})

export class AppComponent { }
