import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { ClustersComponent } from './index';
import { ClusterStep } from './wizard_steps/cluster';

@NgModule({
  declarations: [
    ClustersComponent, ClusterStep
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  entryComponents: [
    ClusterStep
  ],
  exports: [
    ClustersComponent, ClusterStep
  ]
})
export class ClustersModule { }
