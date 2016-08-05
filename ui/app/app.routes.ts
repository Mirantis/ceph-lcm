import {provideRouter, RouterConfig} from '@angular/router';

import {HomeComponent} from './components/home';
import {LoginComponent} from './components/login';
import {DashboardComponent} from './components/dashboard';
import {PageNotFoundComponent} from './components/404';
import {LoggedIn} from './services/session'

export const routes = [
  {path: '', component: HomeComponent, terminal: true},
  {path: 'login', component: LoginComponent},
  {path: 'dashboard', component: DashboardComponent, canActivate: [LoggedIn]},
  {path: '**', component: PageNotFoundComponent}
];

export const APP_ROUTES_PROVIDER = provideRouter(routes);