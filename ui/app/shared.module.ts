import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { Modal, Loader, Filter, Criterion } from './directives';
import { Key, Keys, TrimBy, DateTime, JSONString } from './pipes';

@NgModule({
  imports: [
    BrowserModule, FormsModule
  ],
  declarations: [
    Modal, Loader, Filter, Criterion,
    Keys, Key, TrimBy, DateTime, JSONString
  ],
  exports: [
    Modal, Loader, Filter, Criterion,
    Keys, Key, TrimBy, DateTime, JSONString
  ],
  providers: [
    Modal, Loader, Filter, Criterion
  ]
})
export class SharedModule { }
