import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { AdminComponent, UsersComponent, RolesComponent } from './index';

export const adminRoutes: Routes = [
  {
    path: 'admin', component: AdminComponent, canActivate: [LoggedIn],
    children: [
      {path: 'users', component: UsersComponent, canActivate: [LoggedIn]},
      {path: 'roles', component: RolesComponent, canActivate: [LoggedIn]},
      {path: '**', redirectTo: 'users', pathMatch: 'full'}
    ]
  }
];
