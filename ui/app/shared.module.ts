import { NgModule } from '@angular/core';

import { Modal } from './bootstrap';
import { Key, Keys, TrimBy, DateTime } from './pipes';

@NgModule({
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
