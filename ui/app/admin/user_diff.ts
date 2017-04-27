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

import { Component, Input } from '@angular/core';
import * as _ from 'lodash';

type change = {
  name: string,
  oldValue: string,
  newValue: string
}

@Component({
  selector: 'diff',
  templateUrl: './app/templates/user_diff.html'
})
export class UserDiff {
  @Input() index: number;
  @Input() versions: any[] = [];
  diff: change[] = [];
  currentVersion: any;
  fields = {
    login: 'Login',
    full_name: 'Full Name',
    email: 'Email',
    role_id: 'Role ID'
  };

  ngOnInit() {
    this.currentVersion = this.versions[this.index];

    if (!this.index) return;

    let currentData = this.currentVersion.data;
    let previousData = this.versions[this.index - 1].data;

    _.forEach(this.fields, (name, field) => {
      let [oldValue, newValue] = [currentData[field], previousData[field]];

      console.log(field, oldValue, newValue);
      if (!_.isEqual(oldValue, newValue)) {
        this.diff.push({name, oldValue, newValue});
      }
    });

    console.log(this.diff);
  }
}