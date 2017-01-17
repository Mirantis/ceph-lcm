/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

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
