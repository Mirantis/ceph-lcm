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

import { Token } from '../app/models';

export class MockAuthService {
  login(username: string, password: string) {
    return Promise.resolve(new Token({id: 'f876d8f76s8f68s78fsd8'}));
  }

  logout() {
    return Promise.resolve();
  };

  isLoggedIn() {
    return true;
  }
}
