import * as _ from 'lodash';

import { Injectable } from '@angular/core';
import { DataStore, Record, Mapper } from 'js-data';
import { HttpAdapter } from 'js-data-http';
import { SessionService } from './session';

type supportedMappers = 'auth' | 'user' | 'role' | 'permissions' | 'cluster';

@Injectable()
export class DataService {
  constructor(private session: SessionService) {
    this.store.registerAdapter('http', this.adapter, {default: true});
  }

  store = new DataStore();
  // FIXME: to be moved to configuration
  adapter = new HttpAdapter({basePath: 'http://private-3509f-cephlcmswaggerapi.apiary-mock.com/v1'});
  // adapter = new HttpAdapter({basePath: 'http://private-47d2dd-cephlcm.apiary-mock.com/v1'});
  mappers = {};

  token(): Mapper {return this.getMapper('auth')}
  user(): Mapper {return this.getMapper('user')}
  role(): Mapper {return this.getMapper('role')}
  permissions(): Mapper {return this.getMapper('permissions')}
  cluster(): Mapper {return this.getMapper('cluster')}

  private modelsProperties = {
    auth: {
     user_id: {type: 'string'},
     expires_at: {type: 'number'}
    },
    cluster: {
      name: {type: 'string'},
      execution_id: {type: 'string'},
      configuration: {type: 'object'}
    },
    user: {
      login: {type: 'string'},
      full_name: {type: 'string'},
      time_updated: {type: 'number'},
      email: {type: 'string'}
    },
    role: {
      name: {type: 'string'},
      permissions: {type: 'object'},
    }
  };

  private getMapper(name: supportedMappers): Mapper {
    let mapper: Mapper;
    if (this.mappers.hasOwnProperty(name)) {
      // return cached value
      mapper = this.mappers[name];
    } else {
      // lazily create one
      mapper = this.store.defineMapper(name, {
        endpoint: name,
        schema: _.extend(
          {
            properties: {
              id: {
                 oneOf: [
                   {type: 'string', indexed: true},
                   {type: 'number', indexed: true}
                 ]
              },
              model: {type: 'string'},
              version: {type: 'number'},
              time_updated: {type: 'number'},
              is_deleted: {type: 'boolean'},
              data: {'$ref': '#/definitions/model_data'}
            },
            definitions: {
              model_data: {
                type: 'object',
                properties: this.modelsProperties[name]
              }
            }
          })
      });
      this.mappers[name] = mapper;
    }
    // set authorization header
    // FIXME: Shift to be called in one of Mapper' pre-send hooks
    mapper['headers'] = {
      Authorization: this.session.getToken()
    };
    return mapper;
  }
}