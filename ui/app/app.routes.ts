import { Routes, RouterModule } from '@angular/router';

import {HomeComponent} from './components/home';
import {LoginComponent} from './components/login';
import {DashboardComponent} from './components/dashboard';
import {PageNotFoundComponent} from './404';
import {LoggedIn} from './services/auth';

const appRoutes: Routes = [
  {path: '', component: HomeComponent, terminal: true},
  {path: 'login', component: LoginComponent},
  {path: 'dashboard', component: DashboardComponent, canActivate: [LoggedIn]},
  {path: '**', component: PageNotFoundComponent}
];

export const appRoutingProviders: any[] = [

];

export const routing = RouterModule.forRoot(appRoutes);