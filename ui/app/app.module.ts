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
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app';
import { LoginComponent, DashboardComponent, PasswordResetComponent }  from './dashboard/index';
import { PageNotFoundComponent } from './404';

import { AdminModule } from './admin/admin.module';
import { ClustersModule } from './clusters/clusters.module';
import { ConfigurationsModule } from './configurations/configurations.module';
import { PlaybooksModule } from './playbooks/playbooks.module';
import { ServersModule } from './servers/servers.module';
import { ExecutionsModule } from './executions/executions.module';

import { AuthService, LoggedIn} from './services/auth';
import { SessionService } from './services/session';
import { CookieService } from 'angular2-cookie/core';
import { DataService } from './services/data';
import { ErrorService } from './services/error';

import { appRoutingProviders, routing } from './app.routes';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    PasswordResetComponent,
    DashboardComponent,
    PageNotFoundComponent,
  ],
  imports: [
    routing,
    AdminModule,
    ClustersModule,
    ConfigurationsModule,
    PlaybooksModule,
    ServersModule,
    ExecutionsModule,
    FormsModule,
    BrowserModule,
  ],
  providers: [
    LoggedIn,
    AuthService,
    DataService,
    CookieService,
    SessionService,
    ErrorService,
    appRoutingProviders,
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
