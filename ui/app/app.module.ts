import { NgModule }      from '@angular/core';
import { FormsModule }   from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent }  from './app';
import { LoginComponent, DashboardComponent }  from './dashboard/index';
import { UsersComponent }  from './admin/index';
import { PageNotFoundComponent }  from './404';

import { AdminModule }  from './admin/admin.module';
import { ClustersModule }  from './clusters/clusters.module';
import { ConfigurationsModule }  from './configurations/configurations.module';

import { AuthService, LoggedIn}  from './services/auth';
import { SessionService }  from './services/session';
import { CookieService }  from 'angular2-cookie/core';
import { DataService }  from './services/data';

import { appRoutingProviders, routing } from './app.routes';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    DashboardComponent,
    PageNotFoundComponent
  ],
  imports: [
    routing,
    AdminModule,
    ClustersModule,
    ConfigurationsModule,
    FormsModule,
    BrowserModule
  ],
  providers: [
    LoggedIn,
    AuthService,
    DataService,
    CookieService,
    SessionService,
    appRoutingProviders
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
