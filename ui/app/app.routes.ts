import {provideRouter, RouterConfig} from '@angular/router';

import {HomeComponent} from './components/home';
import {LoginComponent} from './components/login';
import {DashboardComponent} from './components/dashboard';]
import {LoggedIn} from './services/auth'

export const routes = [
  {path: '', component: HomeComponent, terminal: true},
  {path: 'login', component: LoginComponent},
  {path: 'dashboard', component: DashboardComponent, canActivate: [LoggedIn]}
];

export const APP_ROUTES_PROVIDER = provideRouter(routes);