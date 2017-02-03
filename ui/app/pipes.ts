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
import { Pipe, PipeTransform } from '@angular/core';

var formatJSON = require('format-json');

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

@Pipe({name: 'json'})
export class JSONString implements PipeTransform {
  transform(value: Object): string {
    return formatJSON.plain(value);
  }
}

@Pipe({name: 'index'})
export class Index implements PipeTransform {
  transform(value: Object, index: number = 0): any {
    let values: Object[] = _.flatten([value]);
    if (index >= values.length) {
      index = 0;
    }
    return values[index];
  }
}

@Pipe({name: 'deparametrize'})
export class Deparametrize implements PipeTransform {
  transform(value: string = ''): string {
    return _.upperFirst(value.toLowerCase()).split('_').join(' ');
  }
}

@Pipe({name: 'deprefix'})
export class Deprefix implements PipeTransform {
  transform(value: string, prefix: string): string {
    return _.compact(value.replace(prefix, '').split('_')).join(' ');
  }
}
