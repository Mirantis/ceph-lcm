/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { Routes, RouterModule } from '@angular/router';

import { DashboardComponent } from './dashboard/index';
import { LoggedIn } from './services/auth';

import {dashboardRoutes} from './dashboard/index';
import {clustersRoutes} from './clusters/index';
import {configurationsRoutes} from './configurations/index';
import {playbooksRoutes} from './playbooks/index';
import {serversRoutes} from './servers/index';
import {executionsRoutes} from './executions/index';
import {adminRoutes} from './admin/index';

const appRoutes: Routes = [
  ...dashboardRoutes,
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
