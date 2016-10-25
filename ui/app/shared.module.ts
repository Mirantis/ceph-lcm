import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { Modal, Loader, Filter, Criterion, Pager, LongData } from './directives';
import { Key, Keys, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix } from './pipes';

@NgModule({
  imports: [
    BrowserModule, FormsModule
  ],
  declarations: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix
  ],
  exports: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix
  ],
  providers: [
    Modal, Loader, Filter, Criterion, Pager, LongData
  ]
})
export class SharedModule { }
