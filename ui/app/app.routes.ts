import { Routes, RouterModule } from '@angular/router';

import { DashboardComponent, LoginComponent } from './dashboard/index';
import { LoggedIn } from './services/auth';

import {dashboardRoutes} from './dashboard/index';
import {clustersRoutes} from './clusters/index';
import {configurationsRoutes} from './configurations/index';
import {playbooksRoutes} from './playbooks/index';
import {serversRoutes} from './servers/index';
import {executionsRoutes} from './executions/index';
import {adminRoutes} from './admin/index';

import {PageNotFoundComponent} from './404';

const appRoutes: Routes = [
  {path: 'login', component: LoginComponent},
  {
    path: '',
    component: DashboardComponent,
    canActivate: [LoggedIn],
    children: [
      ...clustersRoutes,
      ...configurationsRoutes,
      ...playbooksRoutes,
      ...serversRoutes,
      ...executionsRoutes,
      ...adminRoutes,
      {path: '**', redirectTo: 'clusters'}
    ]
  },
  {path: '**', redirectTo: 'login', pathMatch: 'full'}
];

export const appRoutingProviders: any[] = [];

export const routing = RouterModule.forRoot(appRoutes);