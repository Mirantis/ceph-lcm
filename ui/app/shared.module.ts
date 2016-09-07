import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { Modal } from './bootstrap';
import { Key, Keys, TrimBy, DateTime } from './pipes';

@NgModule({
  imports: [
    BrowserModule
  ],
  declarations: [
    Modal,
    Keys, Key, TrimBy, DateTime
  ],
  exports: [
    Modal,
    Keys, Key, TrimBy, DateTime
  ],
  providers: [
    Modal
  ]
})
export class SharedModule { }
