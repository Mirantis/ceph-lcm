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

function two(value: number): string {
  return ('0' + value).substr(-2);
}

@Pipe({name: 'date_time'})
export class DateTime implements PipeTransform {
  transform(value: number): string {
    var date = new Date(1000 * value);
    return two(date.getDate()) + '/' +
      two(1 + date.getMonth()) + '/' +
      date.getFullYear() + ' ' +
      two(date.getHours()) + ':' +
      two(date.getMinutes()) + ':' +
      two(date.getSeconds());
  }
}