import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

@Pipe({name: 'key'})
export class Key implements PipeTransform {
  transform(value: Object, key: string): any {
    return _.get(value, key, []);
  }
}

@Pipe({name: 'keys'})
export class Keys implements PipeTransform {
  transform(value: Object): any[] {
    return _.keys(value);
  }
}