import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { PlaybooksComponent } from './index';

@NgModule({
  declarations: [
    PlaybooksComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    PlaybooksComponent
  ]
})
export class PlaybooksModule { }
