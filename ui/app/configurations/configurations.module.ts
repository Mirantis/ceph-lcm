import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { ConfigurationsComponent } from './index';
import { SharedModule } from '../shared.module';

@NgModule({
  declarations: [
    ConfigurationsComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    ConfigurationsComponent
  ]
})
export class ConfigurationsModule { }
