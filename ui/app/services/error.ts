import * as _ from 'lodash';
import { Injectable, Output, EventEmitter } from '@angular/core';

@Injectable()
export class ErrorService {
  @Output() errorHappened = new EventEmitter();

  add(error: string, message: string) {
    this.errorHappened.emit({error, message});
  }
}