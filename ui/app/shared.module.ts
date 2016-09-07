import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { Modal, Loader } from './bootstrap';
import { Key, Keys, TrimBy, DateTime } from './pipes';

@NgModule({
  imports: [
    BrowserModule
  ],
  declarations: [
    Modal, Loader,
    Keys, Key, TrimBy, DateTime
  ],
  exports: [
    Modal, Loader,
    Keys, Key, TrimBy, DateTime
  ],
  providers: [
    Modal, Loader
  ]
})
export class SharedModule { }
