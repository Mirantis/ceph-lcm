import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { ClustersComponent } from './index';

@NgModule({
  declarations: [
    ClustersComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule
  ],
  exports: [
    ClustersComponent
  ]
})
export class ClustersModule { }
