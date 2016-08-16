import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';


import { AppComponent }  from './app.component';
import { LoginComponent }  from './dashboard/login';
import { DashboardComponent }  from './dashboard/dashboard';
import { PageNotFoundComponent }  from './404';

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
    BrowserModule,
    routing,
    FormsModule
  ],
  providers: [
    AuthService,
    SessionService,
    CookieService,
    DataService,
    appRoutingProviders,
    LoggedIn
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
