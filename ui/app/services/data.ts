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
import * as $ from 'jquery';

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { DataStore, Record, Mapper } from 'js-data';
import { HttpAdapter } from 'js-data-http';
import { SessionService } from './session';
import { ErrorService } from './error';
import { Token, User, PermissionGroup, Role, Cluster,
  Playbook, PlaybookConfiguration, Server, Execution, ExecutionStep } from '../models';
import { Modal } from '../directives';

type supportedMappers = 'auth' | 'user' | 'role' | 'permission' | 'cluster' |
  'playbook' | 'playbook_configuration' | 'server' | 'execution' | 'execution_step';

export type pagedResult = {
  items: any[],
  page: number,
  per_page: number,
  total: number
};

declare module 'js-data' {
  interface Mapper {
    postCreate(props: Record, opts?: any): Promise<Record>;
    postUpdate(id: string, props: Record, opts?: any): Promise<Record>;
    getVersion(): any;
    getVersions(versionId: string): any;
    getLogs(executionId: string, query?: Object): Promise<pagedResult>;
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
  //basePath = 'http://private-3509f-cephlcmswaggerapi.apiary-mock.com/v1';
  basePath = 'http://localhost:9999/v1';

  adapter = new HttpAdapter({basePath: this.basePath});
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
      id: {type: 'string'},
      hints: {type: 'object'}
    },
    playbook_configuration: {
      name: {type: 'string'},
      playbook: {type: 'string'},
      configuration: {type: 'object'},
      hints: {type: 'object'}
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
          afterFindAll: function(props: any, opts: any, result: any): pagedResult {
            result.items = _.map(result.items, (item, index) => new (this.recordClass)(item));
            return result;
          },
          postCreate(props: any, opts: any = {}): Promise<Record> {
            // Only data: {} should be sent upon object creation
            return this.create(_.get(props, 'data', props), opts);
          },
          postUpdate(id: string, props: any, opts: any = {}): Promise<Record> {
            // All fields are expected on update
            return this.update(id, props);
          },
          getVersions: function(id: string): pagedResult {
            return this.findAll({}, {endpoint: name + '/' + id + '/version'});
          },
          getVersion: function(id: string, versionId: string) {
            return this.find(id, {suffix: '/version/' + versionId});
          },
          getLogs: function(execution_id: string, query: any = {}): Promise<pagedResult> {
            return this.findAll(query, {endpoint: name + '/' + execution_id + '/steps'})
              .then((logs: pagedResult) => {
                logs.items = logs.items as ExecutionStep[];
                return logs as pagedResult;
              });
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

  postJSON(endpoint: string, data: Object): JQueryXHR {
    return $.ajax({
      type: 'POST',
      url: this.basePath + '/' + endpoint,
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify(data)
    });
  }

  handleResponseError(error: any): void {
    var errorCode = 'Error';
    var errorMessage = '';

    if (error) {
      if (error.response) {
        if (error.response.status === 401) {
          this.session.removeToken();
          this.modal.close();
          this.router.navigate(['/login']);
        }
        errorCode = error.response.data.error || error.response.status;
        errorMessage = error.response.data.message || error.response.statusText;
      } else if (error.responseJSON) {
        errorCode = error.responseJSON.error;
        errorMessage = error.responseJSON.message;
      } else {
        errorMessage = (<Error>error).message;
      }
    }
    this.error.add(errorCode, errorMessage);
  }

  downloadExecutionLog(executionId: string): JQueryXHR {
    let url = this.basePath + '/execution/' + executionId + '/log/?download=yes';
    return $.ajax({
      url,
      headers: {
        Authorization: this.session.getToken()
      },
      success: function(result) {
        let data = new Blob([result], {type: 'application/octet-stream'});
        // Making file saving dialog appear with the filename preset
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(data);
        link.download = 'execution.log';
        link.click();
      }
    });
  }
}
