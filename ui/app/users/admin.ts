import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  template: `
<navigation>
  <ul>
    <li> <a [routerLink]="['users']" routerLinkActive='active'>Users</a>
    <li> <a [routerLink]="['roles']" routerLinkActive='active'>Roles</a>
  </ul>
</navigation>

<router-outlet></router-outlet>
`
})
export class AdminComponent {

};