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