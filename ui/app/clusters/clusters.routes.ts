import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { ClustersComponent } from './index';

export const clustersRoutes: Routes = [
  {path: 'clusters', component: ClustersComponent, canActivate: [LoggedIn]}
];
