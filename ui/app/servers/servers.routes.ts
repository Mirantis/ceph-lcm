import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ServersComponent } from './index';

export const serversRoutes: Routes = [
  {path: 'servers', component: ServersComponent, canActivate: [LoggedIn]}
];
