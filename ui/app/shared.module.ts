import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { Modal, Loader } from './bootstrap';
import { Key, Keys, TrimBy, DateTime, JSONString } from './pipes';

@NgModule({
  imports: [
    BrowserModule
  ],
  declarations: [
    Modal, Loader,
    Keys, Key, TrimBy, DateTime, JSONString
  ],
  exports: [
    Modal, Loader,
    Keys, Key, TrimBy, DateTime, JSONString
  ],
  providers: [
    Modal, Loader
  ]
})
export class SharedModule { }
