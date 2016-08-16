import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';


import { AppComponent }  from './app.component';
import { HomeComponent }  from './components/home';
import { LoginComponent }  from './components/login';
import { DashboardComponent }  from './components/dashboard';
import { PageNotFoundComponent }  from './404';

import { AuthService, LoggedIn}  from './services/auth';
import { SessionService }  from './services/session';
import { CookieService }  from 'angular2-cookie/core';
import { DataService }  from './services/data';

import { appRoutingProviders, routing } from './app.routes';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
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
