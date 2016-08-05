import * as _ from 'lodash';
import {Http, Headers, Response} from '@angular/http';
import {AuthService} from './auth';
import {Observable} from 'rxjs/Observable';
import {Injectable} from '@angular/core';

type method = 'get' | 'put' | 'post' | 'delete';

@Injectable()
export class BaseApiService {
  constructor(private http: Http, private authService: AuthService) {
    // _.each(['get', 'put', 'push', 'delete'], (requestMethod: method) => {
    //   _.set(
    //     this,
    //     requestMethod,
    //     (endpoint: string, body: JSON) => this.sendRequest(requestMethod, endpoint, body)
    //   )
    // })
  }

  private sendRequest(requestMethod: method, endpoint: string, body: Object = {}): Promise<any> {
  	let token = this.authService.getToken();
  	let headers = new Headers();
    headers.append('Content-Type', 'application/json');
    if (token) {
    	headers.append('Authentication', token);
    }
  	return this.http[requestMethod](endpoint, body, {headers})
      .map((res: Response) => res.json())
      .map((res: any) => res.data || {})
      .catch((error: any) => {
        return Observable.throw('Internal server error');
      })
      .toPromise();
  }

  get(endpoint: string, body: Object = {}): Promise<any> {
    return this.sendRequest('get', endpoint, body);
  }

  put(endpoint: string, body: Object = {}): Promise<any> {
    return this.sendRequest('put', endpoint, body);
  }

  push(endpoint: string, body: Object = {}): Promise<any> {
    return this.sendRequest('post', endpoint, body);
  }

  delete(endpoint: string, body: Object = {}): Promise<any> {
    return this.sendRequest('delete', endpoint, body);
  }
}