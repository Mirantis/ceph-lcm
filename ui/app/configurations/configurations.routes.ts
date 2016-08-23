import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ConfigurationsComponent } from './index';

export const configurationsRoutes: Routes = [
  {path: 'configurations', component: ConfigurationsComponent, canActivate: [LoggedIn]}
];
