import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { LoginComponent } from './login';
import { PasswordResetComponent } from './password_reset';
import { DashboardComponent } from './dashboard';

export const dashboardRoutes: Routes = [
  {path: 'login', component: LoginComponent},
  {path: 'password_reset', component: PasswordResetComponent},
  {path: 'password_reset/:reset_token', component: PasswordResetComponent}
];
