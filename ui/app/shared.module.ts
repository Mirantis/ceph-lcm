import { NgModule } from '@angular/core';

import { Modal } from './bootstrap';
import { Key, Keys } from './pipes';

@NgModule({
  declarations: [
    Modal,
    Keys, Key
  ],
  exports: [
    Modal,
    Keys, Key
  ],
  providers: [
    Modal
  ]
})
export class SharedModule { }
