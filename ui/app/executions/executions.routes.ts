import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ExecutionsComponent, LogsComponent } from './index';

export const executionsRoutes: Routes = [
  {path: 'executions', component: ExecutionsComponent, canActivate: [LoggedIn]},
  {path: 'executions/:execution_id', component: LogsComponent, canActivate: [LoggedIn]}
];
