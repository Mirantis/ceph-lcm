import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { LoginComponent } from './login';
import { DashboardComponent } from './dashboard';

export const dashboardRoutes: Routes = [
  {path: 'dashboard', component: DashboardComponent, canActivate: [LoggedIn]},
  {path: 'login', component: LoginComponent}
];
