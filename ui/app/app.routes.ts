import { Routes, RouterModule } from '@angular/router';

import {dashboardRoutes} from './dashboard/index';
import {clustersRoutes} from './clusters/index';
import {configurationsRoutes} from './configurations/index';
import {usersRoutes} from './admin/index';

import {PageNotFoundComponent} from './404';

const appRoutes: Routes = [
  ...dashboardRoutes,
  ...clustersRoutes,
  ...configurationsRoutes,
  ...usersRoutes,
  {path: '**', redirectTo: 'dashboard', pathMatch: 'full'}
];

export const appRoutingProviders: any[] = [];

export const routing = RouterModule.forRoot(appRoutes);