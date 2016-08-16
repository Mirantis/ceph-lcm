import { Routes, RouterModule } from '@angular/router';

import {LoginComponent} from './dashboard/login';
import {DashboardComponent} from './dashboard/dashboard';
import {PageNotFoundComponent} from './404';
import {LoggedIn} from './services/auth';

const appRoutes: Routes = [
  {path: 'login', component: LoginComponent},
  {path: '', component: DashboardComponent, canActivate: [LoggedIn]},
  {path: '**', component: PageNotFoundComponent}
];

export const appRoutingProviders: any[] = [

];

export const routing = RouterModule.forRoot(appRoutes);