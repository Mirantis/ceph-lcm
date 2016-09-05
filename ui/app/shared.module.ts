import { NgModule } from '@angular/core';

import { Modal } from './bootstrap';
import { Key, Keys, TrimBy } from './pipes';

@NgModule({
  declarations: [
    Modal,
    Keys, Key, TrimBy
  ],
  exports: [
    Modal,
    Keys, Key, TrimBy
  ],
  providers: [
    Modal
  ]
})
export class SharedModule { }
