import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { ExecutionsComponent, LogsComponent } from './index';

@NgModule({
  declarations: [
    ExecutionsComponent,
    LogsComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    ExecutionsComponent,
    LogsComponent
  ]
})
export class ExecutionsModule { }
