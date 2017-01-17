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
import { Injectable } from '@angular/core';
import { CookieService } from 'angular2-cookie/core';
import { Token } from '../models';

@Injectable()
export class SessionService {
  constructor(private cookieService: CookieService) {}

  tokenKey = 'auth_token';
  userIdKey = 'user_id';

  saveToken(token: Token) {
    let expiration = {
      expires: new Date(token.data.expires_at * 1000)
    };
    this.cookieService.put(this.tokenKey, token.id, expiration);
    this.cookieService.put(this.userIdKey, token.data.user.id, expiration);
  }

  removeToken(): void {
    this.cookieService.remove(this.tokenKey);
  }

  getToken(): string {
    return this.cookieService.get(this.tokenKey);
  }

  getLoggedUserId(): string {
    return this.cookieService.get(this.userIdKey);
  }
}
