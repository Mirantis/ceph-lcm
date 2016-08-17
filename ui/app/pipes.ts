import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash';

@Pipe({name: 'keys'})
export class Keys implements PipeTransform {
  transform(value: number): any[] {
    return _.keys(value);
  }
}