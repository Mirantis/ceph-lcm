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

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { AdminComponent, UsersComponent,
  RolesComponent, PermissionsGroup } from './index';
import { RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep, UserStep } from './wizard_steps/index';

@NgModule({
  declarations: [
    AdminComponent,
    UsersComponent,
    RolesComponent,
    PermissionsGroup,
    RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep, UserStep
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  entryComponents: [
    RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep, UserStep
  ],
  exports: [
    AdminComponent,
    UsersComponent,
    RolesComponent,
    PermissionsGroup,
    RoleNameStep, RoleApiPermissionsStep, RolePlaybookPermissionsStep, UserStep
  ]
})
export class AdminModule { }
