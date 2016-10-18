import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { Modal, Loader, Filter, Criterion, Pager } from './directives';
import { Key, Keys, TrimBy, DateTime, JSONString, Index, Deparametrize } from './pipes';

@NgModule({
  imports: [
    BrowserModule, FormsModule
  ],
  declarations: [
    Modal, Loader, Filter, Criterion, Pager,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize
  ],
  exports: [
    Modal, Loader, Filter, Criterion, Pager,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize
  ],
  providers: [
    Modal, Loader, Filter, Criterion, Pager
  ]
})
export class SharedModule { }
