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