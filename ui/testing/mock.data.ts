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

import { Record } from 'js-data';
import { pagedResult } from '../app/services/data';
import { Cluster, Playbook, PlaybookConfiguration, Server, Execution,
  PermissionGroup, ExecutionStep, Role } from '../app/models';
import * as _ from 'lodash';

function createFakeModelData(index: number): Object {
  return {
    id: 'id' + index,
    name: 'Dummy Name ' + index,
    data: {
      name: 'Dummy Name ' + index,
      execution_id: 'dummy_execution_id_' + index,
      configuration: {
        field1: 'field1',
        field2: 'field2',
        field3: 'field3',
        field4: 'field4'
      }
    }
  }
}

export var amount = 50;
export var itemsPerPage = 10;

export function createFakeData(
  howMany: number,
  Model: {new(params?: Object): Record},
  perPage: number = itemsPerPage
): pagedResult {
  let result = {
    page: 1,
    per_page: perPage,
    total: howMany
  } as pagedResult;
  result.items = _.map(_.range(howMany), (index) => {
    return new Model(createFakeModelData(index));
  });
  return result;
}

export class MockDataService {
  mappers: any[] = [];
  spies: Object = {};

  produceSpies(entityName: string, methodName: string): jasmine.Spy {
    let spyName = entityName + ':' + methodName;
    if (!this.spies[spyName]) {
      this.spies[spyName] = jasmine.createSpy(spyName);
    }
    return this.spies[spyName];
  }

  mapperFactory(Model: {new(params?: Object): Record}, name: string): any {
    if (!this.mappers[name]) {
      this.mappers[name] = {
        findAll: this.produceSpies(name, 'findAll').and.returnValue(
          Promise.resolve(createFakeData(amount, Model))
        ),
        find: this.produceSpies(name, 'find').and.returnValue(
          Promise.resolve(_.head(createFakeData(1, Model).items))
        ),
        postUpdate: this.produceSpies(name, 'postUpdate').and.returnValue(
          Promise.resolve()
        ),
        postCreate: this.produceSpies(name, 'postCreate').and.returnValue(
          Promise.resolve()
        ),
        create: this.produceSpies(name, 'create').and.returnValue(
          Promise.resolve()
        ),
        update: this.produceSpies(name, 'update').and.returnValue(
          Promise.resolve()
        ),
        destroy: this.produceSpies(name, 'destroy').and.returnValue(
          Promise.resolve()
        ),
        getVersions: this.produceSpies(name, 'getVersions').and.returnValue(
          Promise.resolve(createFakeData(10, Model))
        ),
        getVersion: this.produceSpies(name, 'getVersion').and.returnValue(
          Promise.resolve(createFakeData(1, Model).items[0])
        ),
        getLogs: this.produceSpies(name, 'getLogs').and.returnValue(
          Promise.resolve(createFakeData(amount, ExecutionStep))
        )
      };
    }
    return this.mappers[name];
  }

  cluster() {
    return this.mapperFactory(Cluster, 'cluster');
  }

  configuration() {
    return this.mapperFactory(PlaybookConfiguration, 'configuration');
  }

  playbook() {
    return this.mapperFactory(Playbook, 'playbook');
  }

  permission() {
    return this.mapperFactory(PermissionGroup, 'permission');
  }

  server() {
    return this.mapperFactory(Server, 'server');
  }

  role() {
    return this.mapperFactory(Role, 'role');
  }

  execution() {
    return this.mapperFactory(Execution, 'execution');
  }
}
