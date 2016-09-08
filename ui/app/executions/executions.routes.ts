import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ExecutionsComponent } from './index';

export const executionsRoutes: Routes = [
  {path: 'executions', component: ExecutionsComponent, canActivate: [LoggedIn]}
];
