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

@Pipe({name: 'trim_by'})
export class TrimBy implements PipeTransform {
  transform(value: string, by: number): string {
    if (value.length <= by) return value;
    return value.substr(0, by) + '...';
  }
}