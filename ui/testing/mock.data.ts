import { BaseModel } from '../app/models';
import { pagedResult } from '../app/services/data';
import { Cluster } from '../app/models';
import * as _ from 'lodash';

function createFakeModelData(index: number): Object {
  return {
    id: 'id' + index,
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

export function createFakeData(
  howMany: number,
  Model: {new(params?: Object): BaseModel},
  perPage = 10
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

export var amount = 50;

export class MockDataService {
  findAll = jasmine.createSpy('findAll');
  find = jasmine.createSpy('find');
  postCreate = jasmine.createSpy('postCreate');
  postUpdate = jasmine.createSpy('postUpdate');

  mappers: any[] = [];
  mapperFactory(Model: {new(params?: Object): BaseModel}, name: string): any {
    if (this.mappers[name]) return this.mappers[name];
    return {
      findAll: this.findAll.and.returnValue(
        Promise.resolve(createFakeData(amount, Model))
      ),
      find: this.find.and.returnValue(
        Promise.resolve(_.first(createFakeData(1, Model).items))
      ),
      postUpdate: this.postUpdate.and.returnValue(
        Promise.resolve()
      ),
      postCreate: this.postCreate.and.returnValue(
        Promise.resolve()
      ),
      create: this.postCreate.and.returnValue(
        Promise.resolve()
      ),
      update: this.postCreate.and.returnValue(
        Promise.resolve()
      ),
      destroy: this.postCreate.and.returnValue(
        Promise.resolve()
      )
    };
  }

  cluster() {
    return this.mapperFactory(Cluster, 'cluster');
  }
}