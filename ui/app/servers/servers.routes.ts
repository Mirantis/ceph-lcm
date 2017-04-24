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

import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ServersComponent } from './index';

export const serversRoutes: Routes = [
  {
    path: 'servers',
    component: ServersComponent,
    canActivate: [LoggedIn],
    data: {restrictTo: [
      'create_server',
      'view_server',
      'view_server_versions',
      'edit_server',
      'delete_server'
    ]}
  },
  {
    path: 'servers/:server_id',
    component: ServersComponent,
    canActivate: [LoggedIn],
    data: {restrictTo: [
      'view_server',
      'view_server_versions',
      'create_server',
      'edit_server',
      'delete_server'
    ]}
  }
];
