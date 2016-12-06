import * as _ from 'lodash';
import { Component, Input, Output, EventEmitter, SimpleChange, OnChanges } from '@angular/core';

import { ErrorService } from '../services/error';
import { Playbook, Cluster, Server, PlaybookConfiguration, Hint } from '../models';
import globals = require('../services/globals');

@Component({
  selector: 'hint',
  templateUrl: './app/templates/hint.html'
})
export class HintComponent implements OnChanges {
  @Input() scheme: Hint;
  @Output() callback = new EventEmitter();
  value: any;
  result: any;
  isValid: boolean = true;

  ngOnChanges(changes: {[name: string]: SimpleChange}) {
    let schemeChanges = changes['scheme'];
    if (!schemeChanges || !schemeChanges.currentValue || !schemeChanges.isFirstChange) {
      return;
    }
    this.value = schemeChanges.currentValue.value;
    this.onChange();
  }

  validate() {
    this.isValid = true;
    let tempResult: any;
    switch(this.scheme.type) {
      case 'integer':
        tempResult = Math.round(this.value);
        if (1 * this.value !== tempResult) {
          this.isValid = false;
        }
        break;
      case 'boolean':
        tempResult = !!this.value;
        break;
      default:
        tempResult = this.value;
    }
    this.result = tempResult;
  }

  onChange() {
    this.validate();
    this.callback.emit({id: this.scheme.id, value: this.result, isValid: this.isValid});
  }

  isInput() {
    return _.includes(['string', 'integer', 'select'], this.scheme.type);
  }
}