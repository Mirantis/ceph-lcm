import * as _ from 'lodash';

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { DataStore, Record, Mapper } from 'js-data';
import { HttpAdapter } from 'js-data-http';
import { SessionService } from './session';
import { ErrorService } from './error';
import { Token, User, PermissionGroup, Role, Cluster,
  Playbook, PlaybookConfiguration, Server, Execution, ExecutionStep } from '../models';
import { Modal } from '../bootstrap';

type supportedMappers = 'auth' | 'user' | 'role' | 'permission' | 'cluster' |
  'playbook' | 'playbook_configuration' | 'server' | 'execution' | 'execution_step';

declare module 'js-data' {
  interface Mapper {
    postCreate(props: Record, opts?: any): Promise<Record>;
    postUpdate(id: string, props: Record, opts?: any): Promise<Record>;
    getVersion(): any;
    getVersions(versionId: string): any;
    getLogs(executionId: string): Promise<ExecutionStep[]>;
    [key: string]: any;
  }
}

@Injectable()
export class DataService {
  constructor(
    private session: SessionService,
    private error: ErrorService,
    private router: Router,
    private modal: Modal
  ) {
    this.store.registerAdapter('http', this.adapter, {default: true});
  }

  store = new DataStore();

  // FIXME: to be moved to configuration
  adapter = new HttpAdapter({basePath: 'http://private-3509f-cephlcmswaggerapi.apiary-mock.com/v1'});
  // adapter = new HttpAdapter({basePath: 'http://localhost:9999/v1'});
  mappers: {[key: string]: Mapper} = {};

  token(): Mapper {return this.getMapper('auth', Token)}
  user(): Mapper {return this.getMapper('user', User)}
  role(): Mapper {return this.getMapper('role', Role)}
  permission(): Mapper {return this.getMapper('permission', PermissionGroup)}
  cluster(): Mapper {return this.getMapper('cluster', Cluster)}
  playbook(): Mapper {return this.getMapper('playbook', Playbook)}
  configuration(): Mapper {return this.getMapper('playbook_configuration', PlaybookConfiguration)}
  server(): Mapper {return this.getMapper('server', Server)}
  execution(): Mapper {return this.getMapper('execution')}

  private modelsProperties: {[key: string]: Object} = {
    auth: {
     user_id: {type: 'string'},
     expires_at: {type: 'number'}
    },
    cluster: {
      name: {type: 'string'},
      execution_id: {type: 'string'},
      configuration: {type: 'object'}
    },
    playbook: {
      name: {type: 'string'},
      description: {type: 'string'},
      required_server_list: {type: 'boolean'},
      id: {type: 'string'}
    },
    playbook_configuration: {
      name: {type: 'string'},
      playbook: {type: 'string'},
      configuration: {type: 'object'}
    },
    server: {
      name: {type: 'string'},
      fqdn: {type: 'string'},
      ip: {type: 'string'},
      state: {type: 'string'},
      cluster_id: {type: 'string'},
      facts: {type: 'object'}
    },
    execution: {
      playbook_configuration: {type: 'object'},
      state: {type: 'string'}
    },
    execution_step: {
      execution_id: {type: 'string'},
      role: {type: 'string'},
      name: {type: 'string'},
      error: {type: 'string'},
      time_started: {type: 'number'},
      time_finished: {type: 'number'},
      result: {type: 'string'}
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

  private getMapper(name: supportedMappers, recordClass: any = Record): Mapper {
    let mapper: Mapper;
    if (this.mappers.hasOwnProperty(name)) {
      // return cached value
      mapper = this.mappers[name];
    } else {
      // lazily create one
      mapper = this.store.defineMapper(
        name,
        {
          endpoint: name,
          recordClass: recordClass,
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
            }
          ),
          // afterFind: function(props: any, opts: any, result: any) {
          //   return _.map(result.items, (item, index) => new (this.recordClass)(item));
          // },
          afterFindAll: function(props: any, opts: any, result: any) {
            return _.map(result.items, (item, index) => new (this.recordClass)(item));
          },
          postCreate(props: any, opts: any = {}): Promise<Record> {
            // Only data: {} should be sent upon object creation
            return this.create(_.get(props, 'data', props), opts);
          },
          postUpdate(id: string, props: any, opts: any = {}): Promise<Record> {
            // All fields are expected on update
            return this.update(id, props);
          },
          getVersions: function(id: string) {
            return this.findAll({}, {endpoint: name + '/' + id + '/version'});
          },
          getVersion: function(id: string, versionId: string) {
            return this.find(id, {suffix: '/version/' + versionId});
          },
          getLogs: function(execution_id: string): Promise<ExecutionStep[]> {
            return this.findAll({}, {endpoint: name + '/' + execution_id + '/steps'})
              .then((logs: Record[]) => logs as ExecutionStep[]);
          }
        }
      );
      this.mappers[name] = mapper;
    }

    if (name != 'auth') {
      // set authorization header
      // FIXME: Shift to be called in one of Mapper' pre-send hooks
      mapper['headers'] = {
        Authorization: this.session.getToken()
      };
    }
    return mapper;
  }

  handleResponseError(error: any): void {
    var errorCode = 'Error';
    var errorMessage = '';

    if (error && error.response) {
      if (error.response.status === 401) {
        this.session.removeToken();
        this.modal.close();
        this.router.navigate(['/login']);
      }
      errorCode = error.response.data.error || error.response.status;
      errorMessage = error.response.data.message || error.response.statusText;
    } else {
      errorMessage = (<Error>error).message;
    }
    this.error.add(errorCode, errorMessage);
  }
}