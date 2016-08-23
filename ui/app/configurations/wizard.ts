import { Component, Input, Output } from '@angular/core';
import { DataService } from '../services/data';

import { Modal } from '../bootstrap';

import * as _ from 'lodash';

@Component({
  selector: 'wizard',
  templateUrl: './app/templates/wizard.html',
  directives: [Modal]
})
export class WizardComponent {
  step: number = 1;
  @Input() playbooks: Object[];

  newConfiguration: any = {data: {}};
  error: any;

  constructor(private data: DataService, private modal: Modal) {
  }

  forward() {
    this.step += 1;
  }

  backward() {
    this.step -= 1;
  }
}