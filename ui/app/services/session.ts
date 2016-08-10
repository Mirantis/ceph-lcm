import {Injectable} from '@angular/core';
import {CookieService} from 'angular2-cookie/core';
import * as _ from 'lodash';

@Injectable()
export class SessionService {
  constructor(private cookieService: CookieService) {}

  tokenKey = 'auth_token';
  userIdKey = 'user_id';

  saveToken(token: any) {
    this.cookieService.put(this.tokenKey, token.id, {
      expires: new Date(token.data.expires_at * 1000)
    });
    this.cookieService.put(this.userIdKey, token.data.user_id);
  }

  removeToken() {
    this.cookieService.remove(this.tokenKey);
  }

  getToken() {
    return this.cookieService.get(this.tokenKey);
  }

  getLoggedUserId() {
    return this.cookieService.get(this.userIdKey);
  }
}