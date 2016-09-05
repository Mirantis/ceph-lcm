import { Routes } from '@angular/router';
import { LoggedIn } from '../services/auth';
import { PlaybooksComponent } from './index';

export const playbooksRoutes: Routes = [
  {path: 'playbooks', component: PlaybooksComponent, canActivate: [LoggedIn]}
];
