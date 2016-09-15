import * as _ from 'lodash';
import { Record } from 'js-data';

declare module './models' {
  interface BaseModel {
    id: string,
    model: string,
    time_deleted: number,
    time_updated: number,
    initiator_id: string,
    version: number,
    data: any
  }

  interface Token extends BaseModel {
    data: {
      expires_at: number,
      user_id: string
    }
  }

  interface User extends BaseModel {
    data: {
      login: string,
      email: string,
      full_name: string,
      role_id: string
    }
  }

  interface Permissions {
     [key: string]: any
  }

  interface Role extends BaseModel {
    data: {
      name: string,
      permissions: Permissions
    }
  }

  interface Cluster extends BaseModel {
    data: {
      name: string,
      execution_id: string,
      configuration: Object
    }
  }

  interface Playbook extends Record {
    name: string,
    id: string,
    required_server_list: boolean,
    description: string
  }

  interface PlaybookConfiguration extends BaseModel {
    data: {
      name: string,
      playbook: string,
      configuration: Object
    }
  }

  interface Server extends BaseModel {
    data: {
      name: string,
      fqdn: string,
      ip: string,
      state: string,
      cluster_id: string,
      facts: Object
    }
  }

  interface Execution extends BaseModel {
    data: {
      playbook_configuration: {
        id: string,
        version: number
      },
      state: string
    }
  }
}

export class BaseModel extends Record {
  get dateDeleted(): Date {
    return new Date(this.time_deleted);
  }
  set dateDeleted(value: Date) {};

  get dateUpdated(): Date {
    return new Date(this.time_updated);
  }
  set dateUpdated(value: Date) {};

  constructor(props: any) {
    super(props);
    if (!this.data) {
      this.data = {};
    }
  }

  clone(): this {
    return new (<any>this.constructor)(this.toJSON());
  }
}

export class Cluster extends BaseModel {}
export class Token extends BaseModel {}
export class User extends BaseModel {}
export class Role extends BaseModel {}
export class Permissions extends Record {}
export class Playbook extends Record {}
export class PlaybookConfiguration extends BaseModel {}
export class Server extends BaseModel {}
export class Execution extends BaseModel {}
