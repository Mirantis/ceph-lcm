import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { ServersComponent } from './index';

@NgModule({
  declarations: [
    ServersComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    ServersComponent
  ]
})
export class ServersModule { }
